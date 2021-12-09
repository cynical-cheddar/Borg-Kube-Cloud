import json
import math
import sys
import time

import boto3
import os
import subprocess
import logging

import pika
from fabric import task
import requests
import random
import itertools
import string
from dotenv import dotenv_values
import hashlib
import threading

config = dotenv_values("aws/creds.env")

## if on local
##config = dotenv_values("creds.env")
region = config['region']
session = boto3.Session(
    aws_access_key_id=config['aws_access_key_id'],
    aws_secret_access_key=config['aws_secret_access_key'],
    aws_session_token= config['aws_session_token']
)

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body.decode())
    data = str(body.decode())
    ch.basic_ack(delivery_tag=method.delivery_tag)
    sendToEndpoint(data)
    

def SendQueue(name, data):
    # Create a new message
    sqs = session.resource('sqs',  region_name='us-east-1')
    queue = sqs.get_queue_by_name(QueueName=name)


    response = queue.send_message(MessageBody=data)
    # The response is NOT a resource, but gives you a message ID and MD5
    print(response.get('MessageId'))
  #  print(response.get('MD5OfMessageBody'))
    print("sent: " + data )

def sendToEndpoint(data):
    # Create a new message
    
    #SendQueueFifo(name = "ResultQueue.fifo", data = data)
    SendQueue(name = "ResultQueue", data = data)
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

failed = True
connection = None
while(failed):
    try:
        # go do something with the data we have been sent
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='rabbitmq'))
        failed = False
    except:
        print("retry connection")
        failed = True
        time.sleep(5)



channel = connection.channel()
channel.queue_declare(queue='outputQueue', durable=True)
print(' [*] Waiting for messages. To exit press CTRL+C')
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='outputQueue', on_message_callback=callback)
channel.start_consuming()


