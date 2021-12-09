import json
import math
import sys
import time

import boto3

import logging

import pika
from fabric import task
import requests
import random
from dotenv import dotenv_values
config = dotenv_values("aws/creds.env")

region = config['region']
session = boto3.Session(
    aws_access_key_id=config['aws_access_key_id'],
    aws_secret_access_key=config['aws_secret_access_key'],
    aws_session_token= config['aws_session_token']
)






def MakeQueue(name):

    sqs = session.resource('sqs',  region_name=region)
    queue = sqs.create_queue(QueueName=name, Attributes={'DelaySeconds': '1'})


    # You can now access identifiers and attributes
    print(queue.url)
    print(queue.attributes.get('DelaySeconds'))


def SendQueue(name, data):
    # Create a new message
    sqs = session.resource('sqs',  region_name='us-east-1')
    queue = sqs.get_queue_by_name(QueueName=name)


    response = queue.send_message(MessageBody=data)
    # The response is NOT a resource, but gives you a message ID and MD5
    print(response.get('MessageId'))
  #  print(response.get('MD5OfMessageBody'))
    print("sent: " + data )

def SendNumberedStream(name):
    for x in range (0,10000):
        time.sleep(5)
        SendQueue(name, str(x))

instanceMessageDeduplicationId = 0
def SendQueueFifo(name, data):
    global instanceMessageDeduplicationId 
    instanceMessageDeduplicationId += 1
    # Create a new message
    sqs = session.resource('sqs',  region_name=region)
    queue = sqs.get_queue_by_name(QueueName=name)
    response = queue.send_message(MessageBody=str(data), MessageGroupId="1", MessageDeduplicationId=str(instanceMessageDeduplicationId))
    # The response is NOT a resource, but gives you a message ID and MD5
    print(response.get('MessageId'))
    print("sent: " + str(data) )

def GetQueueSize(name):
    print("Accessing Queue: " + name)
    # Get the service resource
    #  sqs = boto3.resource('sqs', region_name='us-east-1')
    # Get the queue
    sqs = session.resource('sqs',  region_name=region)
    queue = sqs.get_queue_by_name(QueueName=name)
    
    n = queue.attributes.get('ApproximateNumberOfMessages')
    print("queue approximately has: " + str(n) + " messages")
    return int(n)

def SendStreamFifo(name, updateInterval):
    global maxSendDuration
    start = time.time()
    j = 0
    rate = 0.1



    maxSendDuration = 2400
    sendInterval1 = 40
    sendBoundary1 = 0

    sendInterval2 = 20
    sendBoundary2 = 120

    sendInterval3 = 10
    sendBoundary3 = 240

    sendInterval4 = 5
    sendBoundary4 = 360

    sendInterval5 = 0.5
    sendBoundary5 = 480

    sendInterval6 = 0.1
    sendBoundary6 = 600

    sendInterval7 = 0.1
    sendBoundary7 = 720

    sendInterval8 = 0.1
    sendBoundary8 = 840

    sendInterval9 = 5
    sendBoundary9 = 960

    sendInterval10 = 20
    sendBoundary10 = 660

    sendInterval11 = 40
    sendBoundary11 = 780
    startTime = time.time()
    while(True):
        elapsedTime = time.time() - startTime 
        waitTime = 0
        if(elapsedTime > sendBoundary1):
            waitTime = sendInterval1
        if(elapsedTime > sendBoundary2):
            waitTime = sendInterval2
        if(elapsedTime > sendBoundary3):
            waitTime = sendInterval3
        if(elapsedTime > sendBoundary4):
            waitTime = sendInterval4
        if(elapsedTime > sendBoundary5):
            waitTime = sendInterval5
        if(elapsedTime > sendBoundary6):
            waitTime = sendInterval6
        if(elapsedTime > sendBoundary7):
            waitTime = sendInterval7
        if(elapsedTime > sendBoundary8):
            waitTime = sendInterval8
        if(elapsedTime > sendBoundary9):
            waitTime = sendInterval9
        if(elapsedTime > sendBoundary10):
            waitTime = sendInterval10
        if(elapsedTime > sendBoundary11):
            waitTime = sendInterval11

        SendQueue("InputQueue", str(random.randint(0,9999)))
        if(time.time() - startTime > maxSendDuration):
            break
        time.sleep(waitTime)

    # for i in range (0,10000):
    #     #send input
    #    # SendQueueFifo(name, str(random.randint(0,9999)))
    #     SendQueue("InputQueue", str(random.randint(0,9999)))
    #     # send to stats
    #    # j += rate
    #    # if(j >= updateInterval):
    #    #     queueSizeRecord = "QUEUE,"
    #    #     queueSize = str(GetQueueSize(name))
    #    #     queueSizeRecord = queueSizeRecord + queueSize + "," + str(time.time())
    #    #     SendQueueFifo("ResultQueue.fifo", queueSizeRecord)
    #    #     j = 0
    #     time.sleep(rate)
    #     if(time.time() - start > maxSendDuration):
    #         break






def CreateEKS():
    client = boto3.client('eks')



def StopInstance(instance_id):
    ec2_client = boto3.client("ec2", region_name="us-east-1")
    response = ec2_client.stop_instances(InstanceIds=[instance_id])
    print(response)

def TerminateInstance(instance_id):
    ec2_client = boto3.resource("ec2", region_name="us-east-1")
    print(ec2_client.Instance(instance_id).terminate())
    
def GetAmountOfInstances():
    ec2_client = boto3.client("ec2", region_name="us-east-1")
    reservations = ec2_client.describe_instances(Filters=[
        {
            "Name": "instance-state-name",
            "Values": ["running"],
        }
    ]).get("Reservations")
    amt = 0
    for reservation in reservations:
        for instance in reservation["Instances"]:
            instance
            amt += amt
    return amt
    
def GetLastInstance():
    ec2_client = boto3.client("ec2", region_name="us-east-1")
    reservations = ec2_client.describe_instances(Filters=[
        {
            "Name": "instance-state-name",
            "Values": ["running"],
        }
    ]).get("Reservations")
    instance_id = 0
    for reservation in reservations:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            instance_type = instance["InstanceType"]
            public_ip = instance["PublicIpAddress"]
            private_ip = instance["PrivateIpAddress"]
            print(f"{instance_id}, {instance_type}, {public_ip}, {private_ip}")
    return instance_id

def StopTopInstance():
    StopInstance(GetLastInstance())
def TerminateTopInstance():
    TerminateInstance(GetLastInstance())


#MakeQueue("LaunchedQueue")
print("launched queue")
time.sleep(60)
print("sending begin")
#SendNumberedStream("LaunchedQueue")
maxSendDuration = 1000

SendStreamFifo("InputQueue.fifo", 5)
#LaunchEC2()
#LaunchNumberedEC2()
#StopTopInstance()
#TerminateTopInstance()
