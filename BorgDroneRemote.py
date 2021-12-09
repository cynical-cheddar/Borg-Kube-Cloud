import json
import math
import sys
import time

import boto3
import os
import subprocess
import logging
import asyncio
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

f = open("aws/instanceid.txt")
myInstanceId = f.read()

## if on local
##config = dotenv_values("creds.env")
region = config['region']
dockerInstanceName = os.environ['HOSTNAME']
print("hostname: " + str(dockerInstanceName))
session = boto3.Session(
    aws_access_key_id=config['aws_access_key_id'],
    aws_secret_access_key=config['aws_secret_access_key'],
    aws_session_token= config['aws_session_token']
)

def GetSpecies(tableName, designation):
    designation = int(designation)
    dbClient = session.resource('dynamodb', region_name=region)
    table = dbClient.Table(tableName)
    response = ""
    try:
        response = table.get_item(Key={'designation': designation})
    except:
        print("error")
        return table.get_item(Key={'designation': 0})
    else:
        return response['Item']

async def AsyncProcessDesignation(data):
    data = str(data)
    chars = string.ascii_lowercase + string.digits + string.ascii_uppercase + string.punctuation
    attempts = 0
    for password_length in range(1, 9):
        for guess in itertools.product(chars, repeat=password_length):
            attempts += 1
            guess = ''.join(guess)
            if guess == data:
                print("species is " + guess + " found in " + str(attempts) + " attempts")
                return guess

async def AsyncGetSpeciesFromDesignation(data):
        designation = int(data)
        species = GetSpecies("species_db", designation)
        info = species['info']
        desirable = info['desirable']
        speciesName = info['species']
        print("desirable: " + str(desirable))
        print("speciesName: " + str(speciesName))
        print("designation: " + str(species['designation']))
        record = str(designation) + "," + speciesName + "," + desirable
        return record

async def asyncCallback(data):
    data = int(data)
    # task1 = asyncio.create_task(
    #     AsyncGetSpeciesFromDesignation(data)
    # )
    # task2 = asyncio.create_task(
    #     AsyncProcessDesignation(data)
    # )
    record = await AsyncGetSpeciesFromDesignation(data)
    await AsyncProcessDesignation(data)
    print("finished asyncCallback")
    return record

def callback(ch, method, properties, body):
    dataType = "DATA," + dockerInstanceName + "@" + str(myInstanceId) + ","
    print(" [x] Received %r" % body.decode())
    data = body.decode()
    data = str(body.decode())

    loop = asyncio.get_event_loop()
    record = loop.run_until_complete(asyncCallback(data))
    
    ch.basic_ack(delivery_tag=method.delivery_tag)
    sendToOutputQueue(dataType+record)
    #loop.close()
    

def sendToOutputQueue(data):
    data = data + "," + str(time.time())
    channel.queue_declare(queue='outputQueue', durable=True)
    message = data
    channel.basic_publish(
        exchange='',
        routing_key='outputQueue',
        body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))
    print(" [x] Sent to phaser %r" % message)


def sendToEndpoint(data):
    # Create a new message
    sqs = session.resource('sqs',  region_name='us-east-1')
    queue = sqs.get_queue_by_name(QueueName="ResultQueue.fifo")


    response = queue.send_message(MessageBody=data)
    # The response is NOT a resource, but gives you a message ID and MD5
    print(response.get('MessageId'))
  #  print(response.get('MD5OfMessageBody'))
    print("sent: " + data )




def id_generator(size=15, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def guess_password(real):
    chars = string.ascii_lowercase + string.digits
    attempts = 0
    for password_length in range(1, 9):
        for guess in itertools.product(chars, repeat=password_length):
            attempts += 1
            guess = ''.join(guess)
            if guess == real:
                print("species is " + guess + " found in " + str(attempts) + " attempts")
                return guess
            # uncomment to display attempts, though will be slower
            #print(guess, attempts)






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
channel.queue_declare(queue='task_queue', durable=True)
print(' [*] Waiting for messages. To exit press CTRL+C')
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='task_queue', on_message_callback=callback)
channel.start_consuming()

#while(1):
#    word = id_generator(size = 5)
#    print("word: " + word)
#    print(guess_password(word))
#    time.sleep(2)




