import os
import json
import math
import sys
import time
import botocore
import boto3
""" :type : pyboto3.s3 """
import paramiko

import logging
import pika
from fabric import task
import requests
import subprocess
import asyncio
from dotenv import dotenv_values
import pika
import threading
from requests import get
import random
config = dotenv_values("aws/creds.env")
## if on local
##config = dotenv_values("creds.env")
region = config['region']

session = boto3.Session(
    aws_access_key_id=config['aws_access_key_id'],
    aws_secret_access_key=config['aws_secret_access_key'],
    aws_session_token= config['aws_session_token']
)
maxWorkerQueueLength = 15
localBuffer = []
localBufferMaxSize = 15
def __init__(self):
        self.start()

def CreateInitScripts():
    # delete init scripts if they exist


    puller = 'sudo docker run -ip 3000:3000 -v "/aws:/aws" 1734673/puller sh -c "python botoPuller.py >>  logfile.txt "\n'
    pusher = 'sudo docker run -ip 3000:3000 -v "/aws:/aws" 1734673/puller sh -c "python botoPusher.py >>  logfile.txt "\n'
    creator = 'sudo docker run -ip 3000:3000 -v "/aws:/aws" 1734673/puller sh -c "python botoCreator.py >>  logfile.txt "\n'
    borgKube = 'sudo python BorgKube.py'

    l1 = "exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1"
    l2 = "echo BEGIN"
    l3 = "sudo mkdir aws"
    l4 = "cd aws"
    l5 = 'echo "region=us-east-1" > creds.env'
    l6 = 'echo ' + '"aws_access_key_id=' + config["aws_access_key_id"] + '" ' +'>> creds.env'
    l7 = 'echo ' + '"aws_secret_access_key=' + config['aws_secret_access_key'] + '" ' +'>> creds.env'
    l8 = 'echo ' + '"aws_session_token=' + config['aws_session_token'] + '" ' +'>> creds.env'
    l9 = 'sudo yum install docker -y'
    l10 = 'sudo service docker start'
    l11 = 'sudo docker pull 1734673/puller'


    lines = ["#!/bin/bash",l1,l2,l3,l4,l5,l6,l7,l8,l9,l10,l11]
    pullerList = lines
    pusherList = lines
    creatorList = lines
    if os.path.exists("initConsumer.sh"):
        os.remove("initConsumer.sh")

    if os.path.exists("initProducer.sh"):
        os.remove("initProducer.sh")

    if os.path.exists("initCreator.sh"):
        os.remove("initCreator.sh")
    if os.path.exists("initBorgKube.sh"):
        os.remove("initBorgKube.sh")

    pullerFile = open("initConsumer.sh", "x", newline='\n')
    for line in pullerList:
        pullerFile.write(line)
        pullerFile.write('\n')
    pullerFile.write(puller)
    pullerFile.write("echo END")
    pullerFile.close()
        
    pusherFile = open("initProducer.sh", "x", newline='\n')
    for line in pusherList:
        pusherFile.write(line)
        pusherFile.write('\n')
    pusherFile.write(pusher)
    pusherFile.write("echo END")
    pusherFile.close()

    creatorFile = open("initCreator.sh", "x", newline='\n')
    for line in creatorList:
        creatorFile.write(line)
        creatorFile.write('\n')
    creatorFile.write(creator)
    creatorFile.write("echo END")
    creatorFile.close()

    borgKubeFile = open("initBorgKube.sh", "x", newline='\n')
    for line in creatorList:
        borgKubeFile.write(line)
        borgKubeFile.write('\n')
    borgKubeFile.write("cd ..")
    borgKubeFile.write(borgKube)
    borgKubeFile.write("echo END")
    borgKubeFile.close()


               



def UpdateLocalBuffer(name):
    print("Accessing Queue: " + name)
    # Get the service resource
  #  sqs = boto3.resource('sqs', region_name='us-east-1')

    # Get the queue
    sqs = session.resource('sqs',  region_name=region)
    queue = sqs.get_queue_by_name(QueueName=name)

    # Process messages by printing out body and optional author name
    for message in queue.receive_messages(MessageAttributeNames=['Author'], MaxNumberOfMessages=10):

        localBuffer.append(message.body)
        # Let the queue know that the message is processed
        message.delete()


# run producer instance
CreateInitScripts()
#bashCommand = 'docker run -ip 3000:3000 -v "D:\Big Data\TestStream\DockerImages\Docker_1\docker_assignment:/aws" 1734673/puller sh -c "python botoPullerLocal.py"'
#process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)





def VinculumControlLoop():
    global maxWorkerQueueLength
    global startTime
    failed = True
    connection = None
    while(failed):
        try:
            # go do something with the data we have been sent
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
            failed = False
        except:
            print("retry connection")
            failed = True
            time.sleep(5)
    
    channel = connection.channel()
    queue = channel.queue_declare(queue='task_queue', durable=True)
    while (True):
       # get length of rabbitmq channel
        current_message_count = queue.method.message_count
       # print(str(current_message_count))
       
       # print(str(count) + " messages in queue")
        print(str(len(localBuffer) )+ " currently in localbuffer")
        print(str(current_message_count)+ " currently in worker queue")
        if(len(localBuffer) >0 ):
            # publish data to local rabbitmq
            message = localBuffer.pop(0)
            channel.basic_publish(
                exchange='',
                routing_key='task_queue',
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ))
            print(" [x] Sent %r" % message)
            time.sleep(sendInterval)
        if(len(localBuffer) < localBufferMaxSize and current_message_count < maxWorkerQueueLength):
           #UpdateLocalBuffer("InputQueue.fifo")
           UpdateLocalBuffer("InputQueue")
           #localBuffer.append(str(random.randint(0,9999)))

        if(time.time() - startTime > maxSendDuration):
            break
       # print("Appended 2x data to local buffer")

#time.sleep(10)
startTime = time.time()
maxSendDuration = 60000
sendInterval = 1
VinculumControlLoop()
print("control loop exited")
