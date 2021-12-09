import json
import math
import sys
import time

import boto3

import logging

import pika
from fabric import task
import requests


from dotenv import dotenv_values
config = dotenv_values("aws/creds.env")

## if on local
##config = dotenv_values("creds.env")
region = config['region']

session = boto3.Session(
    aws_access_key_id=config['aws_access_key_id'],
    aws_secret_access_key=config['aws_secret_access_key'],
    aws_session_token= config['aws_session_token']
)





def GetQueue(name):
    print("Accessing Queue: " + name)
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
        print('Hello, {0}!{1}'.format(message.body, author_text))

        # Let the queue know that the message is processed
        message.delete()
       # time.sleep(0.2)

def CreateEKS():
    client = boto3.client('eks')

def LaunchNumberedEC2():
    LaunchEC2(str(GetAmountOfInstances()))


def LaunchEC2(name='COMSM0072_boto_lab', securitygroup=None):

    logger = logging.getLogger(__name__)
    # this will log boto output to std out
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    ec2 = boto3.resource('ec2',
                         region_name='us-east-1',
                         # pass content of config file as named args
                         **config
                         )

    instances = ec2.create_instances(

        # ImageId='ami-02e136e904f3da870', #(Amazon AMI)
        ImageId='ami-05e4673d4a28889fe',  # (Cloud9 Ubuntu - 2021-10-28T1333)
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        Placement={
            'AvailabilityZone': 'us-east-1a',
        },
        SecurityGroupIds=[securitygroup] if securitygroup else [],
        KeyName='vockey'

    )
    iid = instances[0].id

    # give the instance a tag name
    ec2.create_tags(
        Resources=[iid],
        Tags=[{'Key': 'Name', 'Value': name}]
    )

    logger.info(instances[0])

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
#print("launched queue")
#time.sleep(10)
#print("sending begin")
#SendStream("LaunchedQueue")
while (True):
   # time.sleep(1)
   # print("waiting")
    time.sleep(0.2)
    GetQueue("LaunchedQueue")
#LaunchEC2()
#LaunchNumberedEC2()
#StopTopInstance()
#TerminateTopInstance()