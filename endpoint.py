import json
import math
from os import cpu_count
import sys
import time
import numpy as np
from matplotlib import pyplot as plt
import boto3

import logging

import pika
from fabric import task
import requests


from dotenv import dotenv_values

import sys

printKubeGraphs = False
printEc2Graphs = False


arg = sys.argv[1:]
print(str(arg))
arg = arg[0]
if(str(arg) == "Kube" or str(arg) == "kube"):
  printKubeGraphs = True
  print("print kube graphs set to true")
if(str(arg) == "EC2"):
  printEc2Graphs = True
  print("print ec2 graphs set to true")



config = dotenv_values("aws/creds.env")

## if on local
##config = dotenv_values("creds.env")
region = config['region']

session = boto3.Session(
    aws_access_key_id=config['aws_access_key_id'],
    aws_secret_access_key=config['aws_secret_access_key'],
    aws_session_token= config['aws_session_token']
)

DataMessages = []
CpuMessages = []
DroneMessages = []
InputQueueSizeMessages = []




def GetQueue(name):
  #  print("Accessing Queue: " + name)
    # Get the service resource
  #  sqs = boto3.resource('sqs', region_name='us-east-1')

    # Get the queue
    sqs = session.resource('sqs',  region_name=region)
    queue = sqs.get_queue_by_name(QueueName=name)

    # Process messages by printing out body and optional author name
    for message in queue.receive_messages(MessageAttributeNames=['Author']):
        # Get the custom author message attribute if it was set
        author_text = ''
        if message.message_attributes is not None:
            author_name = message.message_attributes.get('Author').get('StringValue')
            if author_name:
                author_text = ' ({0})'.format(author_name)

        # Print out the body and author (if set)
        print(str(message.body) )
       # f.write(message.body + '\n')
        msgElements = message.body.split(',')
        # based on the type of message, we need to sort it
        if(msgElements[0] == "DATA"):
          DataMessages.append(msgElements)
        if(msgElements[0] == "CPU"):
          CpuMessages.append(msgElements)
        if(msgElements[0] =="DRONE"):
          DroneMessages.append(msgElements)
        if(msgElements[0] == "QUEUE"):
          InputQueueSizeMessages.append(msgElements)
        # Let the queue know that the message is processed
        message.delete()
        if(len(msgElements) > 0):
          return float(msgElements[-1])
        else:
          return 0
       # time.sleep(0.2)

simulationDuration = 1200
simulationTimeout = 2400
#simulationDuration = 60
#simulationTimeout = 120
startTime = time.time()
latestTimestamp = 0
firstTimestamp = 0
while (True):
    latestTimestamp = GetQueue("ResultQueue")
    
    if(firstTimestamp == 0 and latestTimestamp is not None):
      firstTimestamp = latestTimestamp
      print("Found first timestamp: " + str(firstTimestamp))
    elif(len(CpuMessages) > 1 or len(DataMessages)>1):
      if(latestTimestamp is not None and firstTimestamp is not None):
        if(latestTimestamp - firstTimestamp > simulationDuration):
          print("breaking loop")
          break
    if(time.time() - startTime > simulationTimeout):
      break

# sort dataMessages by arrival time
for msg in DataMessages:
  msg[-1] = float(msg[-1])
DataMessages = sorted(DataMessages, key=lambda x: x[-1])

for msg in CpuMessages:
  msg[-1] = float(msg[-1])
CpuMessages = sorted(CpuMessages, key=lambda x: x[-1])

def GetTimeBinRatesAndAxis(timeIntervalSize, DataMessagesLocal, correctStartRate):
  timeBins = []
  firstRecord = DataMessages[0]
  lastRecord = DataMessages[-1]
  startTimestamp = float(firstRecord[-1])
  endTimestamp = float(lastRecord[-1])
  numberOfBins = int(math.ceil(endTimestamp-startTimestamp)/timeIntervalSize)
  DataMessagesFormatted = []

  for record in DataMessagesLocal:
    ts = float(record[-1])
    ts -= startTimestamp
    record[-1] = str(ts)
    DataMessagesFormatted.append(record)

  lastBin = 0
  currentBin = 1
  for i in range (0, int(numberOfBins)):
    timeBin = []
    for record in DataMessagesFormatted:
      # if it's between timeIntervalSize * lastBin and timeIntervalSize * currentBin
      dataTimestamp = float(record[-1])
      if((lastBin*timeIntervalSize) < dataTimestamp and (currentBin * timeIntervalSize) > dataTimestamp):
        timeBin.append(dataTimestamp)
    timeBins.append(timeBin)
    lastBin +=1
    currentBin +=1
  

  # now get the amount of data points in each bin
  timeBinRates = []
  for timeBin in timeBins:
    timeBinRates.append(float(len(timeBin)) / timeIntervalSize)
  # now plot a graph of timebincounts vs time
  xAxisTime = []
  for i in range (0, int(numberOfBins)):
    xAxisTime.append(float(i*timeIntervalSize))#

  if(correctStartRate == True and len(timeBinRates) > 1):
    timeBinRates[0] = 0
  return timeBinRates, xAxisTime
## =================================================DATA STUFF==================================##

## get drone creation info 

############################################# KUBE ################################################

droneCreateTimestamps = []
droneDestroyTimestamps = []
defaultCreateValues = []
defaultDestroyValues = []
for record in DroneMessages:
  if(record[1] == "CREATED"):
    droneCreateTimestamps.append(float(record[-1]))
  if(record[1] == "DESTROYED"):
    droneDestroyTimestamps.append(float(record[-1]))

for i in range (0, len(droneDestroyTimestamps)):
  droneDestroyTimestamps[i] -= firstTimestamp
  defaultDestroyValues.append(0.0)
for i in range (0, len(droneCreateTimestamps)):
  droneCreateTimestamps[i] -= firstTimestamp
  defaultCreateValues.append(0.0)

# get overall rate of data flow over time
timeIntervalSize = 10.0

if(printKubeGraphs):
# get data messages for each drone
  droneOneDataMessages = []
  droneTwoDataMessages = []
  droneThreeDataMessages = []
  droneFourDataMessages = []
  droneFiveDataMessages = []
  droneSixDataMessages = []
  droneSevenDataMessages = []
  droneEightDataMessages = []
  droneNineDataMessages = []
  droneTenDataMessages = []
  for record in DataMessages:
    droneName = str(record[1])
    if(droneName[0]=="1"):
      droneOneDataMessages.append(record)
    if(droneName[0]=="2"):
      droneTwoDataMessages.append(record)
    if(droneName[0]=="3"):
      droneThreeDataMessages.append(record)
    if(droneName[0]=="4"):
      droneFourDataMessages.append(record)
    if(droneName[0]=="5"):
      droneFiveDataMessages.append(record)
    if(droneName[0]=="6"):
      droneSixDataMessages.append(record)
    if(droneName[0]=="7"):
      droneSevenDataMessages.append(record)
    if(droneName[0]=="8"):
      droneEightDataMessages.append(record)
    if(droneName[0]=="9"):
      droneNineDataMessages.append(record)
    if(droneName[0]=="10"):
      droneTenDataMessages.append(record)

  # whole kube
  timeBinRates, xAxisTime = GetTimeBinRatesAndAxis(timeIntervalSize, DataMessages, False)
  plt.plot(xAxisTime, timeBinRates, label = "Total Throughput")
  # drone 1
  timeBinRatesDrone1, xAxisTimeDrone1 = GetTimeBinRatesAndAxis(timeIntervalSize, droneOneDataMessages, False)
  print(str(droneOneDataMessages))
  plt.plot(xAxisTimeDrone1, timeBinRatesDrone1, label = "Drone 1", dashes=[6, 2])
  # drone 2
  timeBinRatesDrone2, xAxisTimeDrone2 = GetTimeBinRatesAndAxis(timeIntervalSize, droneTwoDataMessages, True)
  if(sum(timeBinRatesDrone2)>0):
    plt.plot(xAxisTimeDrone2, timeBinRatesDrone2, label = "Drone 2", dashes=[2, 2])
  # drone 3
  timeBinRatesDrone3, xAxisTimeDrone3 = GetTimeBinRatesAndAxis(timeIntervalSize, droneThreeDataMessages, True)
  if(sum(timeBinRatesDrone3)>0):
    plt.plot(xAxisTimeDrone3, timeBinRatesDrone3, label = "Drone 3", dashes=[1, 1])
  # drne 4
  timeBinRatesDrone4, xAxisTimeDrone4 = GetTimeBinRatesAndAxis(timeIntervalSize, droneFourDataMessages, True)
  if(sum(timeBinRatesDrone4)>0):
    plt.plot(xAxisTimeDrone4, timeBinRatesDrone4, label = "Drone 4", dashes=[2, 2, 10, 2])
  # drone 5
  timeBinRatesDrone5, xAxisTimeDrone5 = GetTimeBinRatesAndAxis(timeIntervalSize, droneFiveDataMessages, True)
  if(sum(timeBinRatesDrone5)>0):
    plt.plot(xAxisTimeDrone5, timeBinRatesDrone5, label = "Drone 5", dashes=[2, 6, 10, 6])
  # drone 6
  timeBinRatesDrone6, xAxisTimeDrone6 = GetTimeBinRatesAndAxis(timeIntervalSize, droneSixDataMessages, True)
  if(sum(timeBinRatesDrone6)>0):
    plt.plot(xAxisTimeDrone6, timeBinRatesDrone6, label = "Drone 6", dashes=[1, 4, 1, 4])
  # drone 7
  timeBinRatesDrone7, xAxisTimeDrone7 = GetTimeBinRatesAndAxis(timeIntervalSize, droneSevenDataMessages, True)
  if(sum(timeBinRatesDrone7)>0):
    plt.plot(xAxisTimeDrone7, timeBinRatesDrone7, label = "Drone 7", dashes=[4, 1, 4, 1])
  # drone 8
  timeBinRatesDrone8, xAxisTimeDrone8 = GetTimeBinRatesAndAxis(timeIntervalSize, droneEightDataMessages, True)
  if(sum(timeBinRatesDrone8)>0):
    plt.plot(xAxisTimeDrone8, timeBinRatesDrone8, label = "Drone 8", dashes=[10, 10, 2, 10])
  # drone 9
  timeBinRatesDrone9, xAxisTimeDrone9 = GetTimeBinRatesAndAxis(timeIntervalSize, droneNineDataMessages, True)
  if(sum(timeBinRatesDrone9)>0):
    plt.plot(xAxisTimeDrone9, timeBinRatesDrone9, label = "Drone 9")
  # drone 10
  timeBinRatesDrone10, xAxisTimeDrone10 = GetTimeBinRatesAndAxis(timeIntervalSize, droneTenDataMessages, True)
  if(sum(timeBinRatesDrone10)>0):
    plt.plot(xAxisTimeDrone10, timeBinRatesDrone10, label = "Drone 10")

  #plt.scatter(droneCreateTimestamps, defaultCreateValues, c = "blue", label = "Drone Created")
  #plt.scatter(droneDestroyTimestamps, defaultDestroyValues, c = "orange", label = "Drone Destroyed")
  plt.scatter([0], [0], c = "orange", label = "Drone Destroyed")
  plt.scatter([0], [0], c = "blue", label = "Drone Created")

  #
  plt.xlabel('Simulation Time / (s)')
  plt.ylabel('Throughput rate / per second')
  plt.title('Data Throughput of Local Kube Cluster - 0.167Hz Input Rate for 240 seconds')
  plt.legend(loc='upper right')

  plt.show()

############################################# EC2 ###############################################
## PLOT A GRAPH OF time vs message queue size
if(printEc2Graphs):
  queueSizeTimes = []
  queueSizes = []
  for sizeRecord in InputQueueSizeMessages:
    sizeTimestamp = float(sizeRecord[-1])
    sizeTimestamp -= firstTimestamp
    queueSizeTimes.append(sizeTimestamp)
    queueSizes.append(float(sizeRecord[1]))

  plt.plot(queueSizeTimes, queueSizes, label = "Input Queue Buffer Size")
  plt.title('Input Queue Buffer Size - 4Hz Input Rate for 600 seconds')
  plt.xlabel('Simulation Time / (s)')
  plt.ylabel('Input Queue Buffer Size')
  plt.legend(loc='upper right')
  plt.show()

  # now get a list of unique instance id names
  instanceIds = []
  for dm  in DataMessages:
    droneAndEC2 = str(dm[1])
    droneAndEC2List = droneAndEC2.split("@")
    EC2_id = droneAndEC2List[1]
    # see if ec2 id is in instance ids
    if(instanceIds.count(EC2_id) == 0):
      instanceIds.append(EC2_id)

  print("Unique instance ids: " + str(instanceIds))

  AllMessages = []
  EC2_OneDataMessages = []
  EC2_TwoDataMessages = []
  EC2_ThreeDataMessages = []
  EC2_FourDataMessages = []
  EC2_FiveDataMessages = []
  EC2_SixDataMessages = []
  EC2_SevenDataMessages = []
  EC2_EightDataMessages = []
  EC2_NineDataMessages = []
  EC2_TenDataMessages = []

  def extractEC2_id(name):
    droneAndEC2 = str(name)
    droneAndEC2List = droneAndEC2.split("@")
    EC2_id = droneAndEC2List[1]
    return EC2_id

  for dm in DataMessages:
    newDm = dm
    AllMessages.append(newDm)
    ec2_name = str(extractEC2_id(dm[1]))
    if(ec2_name == instanceIds[0]):
      EC2_OneDataMessages.append(newDm)
    if(len(instanceIds) > 1):
      if(ec2_name == instanceIds[1]):
        EC2_TwoDataMessages.append(newDm)
    if(len(instanceIds)> 2):
      if(ec2_name == instanceIds[2]):
        EC2_ThreeDataMessages.append(newDm)
    if(len(instanceIds)> 3):
      if(ec2_name == instanceIds[3]):
        EC2_FourDataMessages.append(newDm)
    if(len(instanceIds)> 4):
      if(ec2_name == instanceIds[4]):
        EC2_FiveDataMessages.append(newDm)
    if(len(instanceIds)> 5):
      if(ec2_name == instanceIds[5]):
        EC2_SixDataMessages.append(newDm)
    if(len(instanceIds)> 6):
      if(ec2_name == instanceIds[6]):
        EC2_SevenDataMessages.append(newDm)
    if(len(instanceIds)> 7):
      if(ec2_name == instanceIds[7]):
        EC2_EightDataMessages.append(newDm)
    if(len(instanceIds)> 8):
      if(ec2_name == instanceIds[8]):
        EC2_NineDataMessages.append(newDm)
    if(len(instanceIds)> 9):
      if(ec2_name == instanceIds[9]):
        EC2_TenDataMessages.append(newDm)

  print("all messages: " + str(AllMessages))
  timeBinRates, xAxisTime = GetTimeBinRatesAndAxis(timeIntervalSize, AllMessages, False)
  plt.plot(xAxisTime, timeBinRates, label = "Total Architecture Throughput")
  
  # ec2 1
  print("EC2_OneDataMessages " + str(EC2_OneDataMessages))
  timeBinRatesEC2_1, xAxisTimeDrone1 = GetTimeBinRatesAndAxis(timeIntervalSize, EC2_OneDataMessages, True)
  print("timeBinRatesEC2_1 " + str(timeBinRatesEC2_1))
  print(str(timeBinRatesEC2_1))
  plt.plot(xAxisTimeDrone1, timeBinRatesEC2_1, label = "EC2 1", dashes=[6, 2])
  # drone 2
  timeBinRatesEC2_2, xAxisTimeDrone2 = GetTimeBinRatesAndAxis(timeIntervalSize, EC2_TwoDataMessages, True)
  print("ec2 two data messages " + str(EC2_TwoDataMessages))
  print(str(timeBinRatesEC2_2))
  if(sum(timeBinRatesEC2_2)>0):
    plt.plot(xAxisTimeDrone2, timeBinRatesEC2_2, label = "EC2 2", dashes=[2, 2])
  # drone 3
  timeBinRatesEC2_3, xAxisTimeDrone3 = GetTimeBinRatesAndAxis(timeIntervalSize, EC2_ThreeDataMessages, True)
  if(sum(timeBinRatesEC2_3)>0):
    plt.plot(xAxisTimeDrone3, timeBinRatesEC2_3, label = "EC2 3", dashes=[1, 1])

  timeBinRatesEC2_4, xAxisTimeDrone4 = GetTimeBinRatesAndAxis(timeIntervalSize, EC2_FourDataMessages, True)
  if(sum(timeBinRatesEC2_4)>0):
    plt.plot(xAxisTimeDrone4, timeBinRatesEC2_4, label = "EC2 4", dashes=[7, 7])

  timeBinRatesEC2_5, xAxisTimeDrone5 = GetTimeBinRatesAndAxis(timeIntervalSize, EC2_FiveDataMessages, True)
  if(sum(timeBinRatesEC2_5)>0):
    plt.plot(xAxisTimeDrone5, timeBinRatesEC2_5, label = "EC2 5", dashes=[9, 9])

  timeBinRatesEC2_6, xAxisTimeDrone6 = GetTimeBinRatesAndAxis(timeIntervalSize, EC2_SixDataMessages, True)
  if(sum(timeBinRatesEC2_6)>0):
    plt.plot(xAxisTimeDrone6, timeBinRatesEC2_6, label = "EC2 6", dashes=[1, 2, 1])

  timeBinRatesEC2_7, xAxisTimeDrone7 = GetTimeBinRatesAndAxis(timeIntervalSize, EC2_SevenDataMessages, True)
  if(sum(timeBinRatesEC2_7)>0):
    plt.plot(xAxisTimeDrone7, timeBinRatesEC2_7, label = "EC2 6", dashes=[3, 1, 3])


  plt.scatter([0], [0], c = "orange", label = "EC2 Destroyed")
  plt.scatter([0], [0], c = "blue", label = "EC2 Created")


  plt.xlabel('Simulation Time / (s)')
  plt.ylabel('Throughput rate / per second')
  plt.title('Data Throughput of Architecture -  4Hz Input Rate for 600 seconds')
  plt.legend(loc='upper right')

  plt.show()
    

# cpu schema: CPUtag, HOST, core n, timestamp
## =================================================CPU STUFF===================================##
hostCpuValues = []
hostCpuTimestamps = []

# host
for record in CpuMessages:
  hostPercent = record[1]
  timestamp = record[-1]
  hostCpuValues.append(float(hostPercent))
  hostCpuTimestamps.append(float(timestamp))

drone1cpuValues = []
drone2cpuValues = []
drone3cpuValues = []
drone4cpuValues = []
drone5cpuValues = []
drone6cpuValues = []
drone7cpuValues = []
drone8cpuValues = []
drone9cpuValues = []
drone10cpuValues = []




# drone 1
for record in CpuMessages:
  # if length of record is greater than 3
  if(len(record) > 3):
    dronePercent = record[2]
    drone1cpuValues.append(float(dronePercent))
  else:
    drone1cpuValues.append(float(0))
  if(len(record) > 4):
    dronePercent = record[3]
    drone2cpuValues.append(float(dronePercent))
  else:
    drone2cpuValues.append(float(0))
  if(len(record) > 5):
    dronePercent = record[4]
    drone3cpuValues.append(float(dronePercent))
  else:
    drone3cpuValues.append(float(0))
  if(len(record) > 6):
    dronePercent = record[5]
    drone4cpuValues.append(float(dronePercent))
  else:
    drone4cpuValues.append(float(0))
  if(len(record) > 7):
    dronePercent = record[6]
    drone5cpuValues.append(float(dronePercent))
  else:
    drone5cpuValues.append(float(0))
  if(len(record) > 8):
    dronePercent = record[7]
    drone6cpuValues.append(float(dronePercent))
  else:
    drone6cpuValues.append(float(0))
  if(len(record) > 9):
    dronePercent = record[8]
    drone7cpuValues.append(float(dronePercent))
  else:
    drone7cpuValues.append(float(0))
  if(len(record) > 10):
    dronePercent = record[9]
    drone8cpuValues.append(float(dronePercent))
  else:
    drone8cpuValues.append(float(0))
  if(len(record) > 11):
    dronePercent = record[10]
    drone9cpuValues.append(float(dronePercent))
  else:
    drone9cpuValues.append(float(0))
  if(len(record) > 12):
    dronePercent = record[11]
    drone10cpuValues.append(float(dronePercent))
  else:
    drone10cpuValues.append(float(0))

firstTimestamp = hostCpuTimestamps[0]


# subtract first timestamp of list from all elements
for i in range (0, len(hostCpuTimestamps)):
  hostCpuTimestamps[i] -= firstTimestamp



if(printKubeGraphs):
  plt.plot(hostCpuTimestamps, hostCpuValues, c = "blue", label = "Host CPU Utilisation")
  plt.plot(hostCpuTimestamps, drone1cpuValues, c = "red", label = "Drone 1 CPU Utilisation" , dashes=[6, 2])
  if(sum(drone2cpuValues) > 10):
    plt.plot(hostCpuTimestamps, drone2cpuValues, c = "green", label = "Drone 2 CPU Utilisation", dashes=[2, 2])
  if(sum(drone3cpuValues) > 10):
    plt.plot(hostCpuTimestamps, drone3cpuValues, c = "cyan", label = "Drone 3 CPU Utilisation" , dashes=[1, 1])
  if(sum(drone4cpuValues) > 10):
    plt.plot(hostCpuTimestamps, drone4cpuValues, c = "yellow", label = "Drone 4 CPU Utilisation" , dashes=[2, 2, 10, 2])
  if(sum(drone5cpuValues) > 10):
    plt.plot(hostCpuTimestamps, drone5cpuValues, c = "magenta", label = "Drone 5 CPU Utilisation", dashes=[2, 6, 10, 6])
  if(sum(drone6cpuValues) > 10):
    plt.plot(hostCpuTimestamps, drone6cpuValues, c = "black", label = "Drone 6 CPU Utilisation", dashes=[1, 4, 1, 4])
  if(sum(drone7cpuValues) > 10):
    plt.plot(hostCpuTimestamps, drone7cpuValues, c = "gold", label = "Drone 7 CPU Utilisation", dashes=[4, 1, 4, 1])
  if(sum(drone8cpuValues) > 10):
    plt.plot(hostCpuTimestamps, drone8cpuValues, c = "crimson", label = "Drone 8 CPU Utilisation" , dashes=[10, 10, 2, 10])
  if(sum(drone9cpuValues) > 10):
    plt.plot(hostCpuTimestamps, drone9cpuValues, c = "indigo", label = "Drone 9 CPU Utilisation")
  if(sum(drone10cpuValues) > 10):
    plt.plot(hostCpuTimestamps, drone10cpuValues, c = "black", label = "Drone 10 CPU Utilisation")
  plt.scatter([0], [0], c = "orange", label = "Drone Destroyed")
  plt.scatter([0], [0], c = "blue", label = "Drone Created")


  plt.xlabel('Simulation Time / (s)')
  plt.ylabel('CPU Utilisation / (%)')
  plt.title('Host Machine and Docker Worker Drone CPU Utilisation Over Time - 0.167Hz Rate for 240 seconds')
  plt.legend(loc='upper right')
  plt.show()