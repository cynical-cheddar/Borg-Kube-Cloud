import json
import math
import sys
import time

import boto3

import logging

import pika
from fabric import task
import requests
import os

from dotenv import dotenv_values
config = dotenv_values("aws/creds.env")
## if on local
##config = dotenv_values("creds.env")
region = config['region']
securityGroup = config['sg']

session = boto3.Session(
    aws_access_key_id=config['aws_access_key_id'],
    aws_secret_access_key=config['aws_secret_access_key'],
    aws_session_token= config['aws_session_token']
)


def CreateInitScripts():
    # delete init scripts if they exist


    puller = 'sudo docker run -ip 3000:3000 -v "/aws:/aws" 1734673/puller sh -c "python botoPuller.py >>  logfile.txt "\n'
    pusher = 'sudo docker run -ip 3000:3000 -v "/aws:/aws" 1734673/puller sh -c "python botoPusher.py >>  logfile.txt "\n'
    creator = 'sudo docker run -ip 3000:3000 -v "/aws:/aws" 1734673/puller sh -c "python botoCreator.py >>  logfile.txt "\n'
    borgKube = 'sudo python3 BorgKube.py'

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
    l12 = 'sudo docker network create -d bridge myapp_net'

    lines = ["#!/bin/bash",l1,l2,l3,l4,l5,l6,l7,l8,l9,l10,l11,l12]
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
    borgKubeFile.write("cd ..\n")
    borgKubeFile.write("wget https://borg-kube-bucket2.s3.amazonaws.com/BorgKube.py")
    borgKubeFile.write("\n")
    borgKubeFile.write("sudo yum install pip3 -y\n")
    #borgKubeFile.write("pip3 install psutil\n")
    #borgKubeFile.write("pip3 install docker\n")
    #borgKubeFile.write("pip3 install boto3\n")
    #borgKubeFile.write("pip3 install python-dotenv\n")
    #borgKubeFile.write("pip3 install botocore\n")
    borgKubeFile.write("pip3 install psutil docker boto3 python-dotenv botocore\n")
    borgKubeFile.write("sudo gpasswd -a $USER docker\n")
    borgKubeFile.write("sudo chmod 666 /var/run/docker.sock\n")
    borgKubeFile.write(borgKube + "\n")
    borgKubeFile.write("echo END")
    borgKubeFile.close()

def CreateOnQueueCommand(name):
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
        print(message.body)
        msg = message.body
        message.delete()
        # create n puller instances
        if(int(msg) >0):
            for i in range(0, int(msg)):
                
                LaunchBorgKube(name = "Kube", n = 1)
        # delete n puller instances
        elif (int(msg) < 0):
            amt = - int(msg)
            StopBorgKube(name = "Kube", n = 1)
               

        
def StopBorgKube(name = "Kube", n = 1):
    ec2 = session.resource('ec2', region_name=region)
    i = 0 
    iids = []
    for instance in ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]):
        print("instance " + str(instance))
        if(instance.tags is not None):
            print(str(instance.tags))
            print("type "+ str(type(instance.tags)))
            print(str(instance.tags[0]))
            print("type "+ str(type(instance.tags[0])))
            tags = instance.tags[0]
            if(tags['Value']== name):
                iids.append(instance.id)
                i += 1
            
                
    if(len(iids) > 0 and i > 1):
        print("found iid to kill")
    #    ec2_client = session.resource("ec2", region_name="us-east-1")
        TerminateInstance(iids[0])
        print("KILLED CONSUMER")
    print("end StopBorgKube")


    


def LaunchBorgKube(name='Kube', n = 1):

    if(GetAmountOfInstances() < 9):
        borgKubeInit = open('initBorgKube.sh')
        logger = logging.getLogger(__name__)
        # this will log boto output to std out
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)

        ec2 = session.resource('ec2', region_name=region)
        
        instances = ec2.create_instances(

            ImageId='ami-02e136e904f3da870', #(Amazon AMI)
        #  ImageId='ami-0d1a4d53e40abecc4',  
            MinCount=1,
            MaxCount=1,
            InstanceType='m5.large',
            Placement={
                'AvailabilityZone': 'us-east-1a',
            },
            SecurityGroupIds=[securityGroup],
            KeyName='educate-us-east-second',
            # change to shell puller for old version
            UserData = borgKubeInit.read()
        )
        iid = instances[0].id

        

        logger.info(instances[0])


        print('Instance id just created:', iid)
        
    #   print('Instances in the SSM instances list right now:')


        i = ec2.Instance(id= iid)
        
        print("launching instance")
        i.wait_until_running()
        time.sleep(10)
        # give the instance a tag name
        ec2.create_tags(
            Resources=[iid],
            Tags=[{'Key': 'Name', 'Value': name}]
        )
        borgKubeInit.close()

def StopInstance(instance_id):
    ec2_client = session.resource("ec2", region_name="us-east-1")
    response = ec2_client.stop_instances(InstanceIds=[instance_id])
    print(response)

def TerminateInstance(instance_id):
    ec2_client = session.resource("ec2", region_name="us-east-1")
    print(ec2_client.Instance(instance_id).terminate())
    
def GetAmountOfInstances():
    ec2_client = session.resource("ec2", region_name="us-east-1")
    reservations = ec2_client.instances.filter(Filters=[
        {
            "Name": "instance-state-name",
            "Values": ["running"],
        }
    ])
    amt = 0
    for reservation in reservations:
        amt += amt
    return amt
    
def GetLastInstance():
    ec2_client = session.resource("ec2", region_name="us-east-1")
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


CreateInitScripts()
shellPuller = open('initConsumer.sh')
borgKubeInit = open('initBorgKube.sh')

while (True):
    time.sleep(0.4)
    CreateOnQueueCommand("CreatorQueue.fifo")
