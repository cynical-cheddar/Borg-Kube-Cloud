import collections
import os
import json
import math
import random
import sys
import time
import botocore
import boto3
from pika import spec
import random

""" :type : pyboto3.s3 """
import paramiko
import subprocess
import logging

import pika
from fabric import task
import requests

from dotenv import dotenv_values


instanceMessageDeduplicationId = 0

config = dotenv_values("creds.env")
## remote
#config = dotenv_values("aws/creds.env")
region = config['region']
securityGroup = config['sg']
session = boto3.Session(
    aws_access_key_id=config['aws_access_key_id'],
    aws_secret_access_key=config['aws_secret_access_key'],
    aws_session_token= config['aws_session_token']
)

botoClient = boto3.client(
    's3',
    aws_access_key_id=config['aws_access_key_id'],
    aws_secret_access_key=config['aws_secret_access_key'],
    aws_session_token= config['aws_session_token']
)

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
            if( i >= n):
                break
    if(len(iids) > 0):
        print("found iid to kill")
    #    ec2_client = session.resource("ec2", region_name="us-east-1")
        TerminateInstance(iids[0])
        print("KILLED CONSUMER")
    print("end StopBorgKube")

def LaunchBorgKube(name='Kube', n = 1):

    if(True):
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
        time.sleep(20)
        # give the instance a tag name
        

        logger.info(instances[0])


        print('Instance id just created:', iid)
        
    #   print('Instances in the SSM instances list right now:')


        i = ec2.Instance(id= iid)
        
        print("launching instance")
        print("launched botg kube")
        i.wait_until_running()
        time.sleep(10)
        ec2.create_tags(
            Resources=[iid],
            Tags=[{'Key': 'Name', 'Value': name}]
        )
       # time.sleep(20)
        borgKubeInit.close()


def LaunchProducer(name='Producer'):
    logger = logging.getLogger(__name__)
    # this will log boto output to std out
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    ec2 = session.resource('ec2', region_name=region)

    instances = ec2.create_instances(

         ImageId='ami-02e136e904f3da870', #(Amazon AMI)
       #  ImageId='ami-0d1a4d53e40abecc4',  
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        Placement={
            'AvailabilityZone': 'us-east-1a',
        },
        SecurityGroupIds=[securityGroup],
        KeyName='educate-us-east-second',
        UserData = shellPusher.read()
    )
    iid = instances[0].id

    # give the instance a tag name
    #ec2.create_tags(
    #    Resources=[iid],
    #    Tags=[{'Key': 'Name', 'Value': name}]
    #)
    logger.info(instances[0])
    
    print('Instance id just created:', iid)

def LaunchConsumer(name='ConsumerMk1'):
    logger = logging.getLogger(__name__)
    # this will log boto output to std out
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    ec2 = session.resource('ec2', region_name=region)

    instances = ec2.create_instances(

         ImageId='ami-02e136e904f3da870', #(Amazon AMI)
       #  ImageId='ami-0d1a4d53e40abecc4',  
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        Placement={
            'AvailabilityZone': 'us-east-1a',
        },
        SecurityGroupIds=[securityGroup],
        KeyName='educate-us-east-second',
        UserData = shellKube.read()
    )
    iid = instances[0].id

    # give the instance a tag name
    #ec2.create_tags(
    #    Resources=[iid],
    #    Tags=[{'Key': 'Name', 'Value': name}]
    #)
    logger.info(instances[0])
    print('Instance id just created:', iid)

def LaunchCreator(name='creator'):
    logger = logging.getLogger(__name__)
    # this will log boto output to std out
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    ec2 = session.resource('ec2', region_name=region)
    
    instances = ec2.create_instances(

        ImageId='ami-02e136e904f3da870', #(Amazon AMI)
       #  ImageId='ami-0d1a4d53e40abecc4',  
        MinCount=1,
        MaxCount=1,
        InstanceType='t3.micro',
        Placement={
            'AvailabilityZone': 'us-east-1a',
        },
        SecurityGroupIds=[securityGroup],
        KeyName='educate-us-east-second',
        UserData = shellCreator.read()
    )
    iid = instances[0].id

    # give the instance a tag name
    #ec2.create_tags(
    #    Resources=[iid],
    #    Tags=[{'Key': 'Name', 'Value': name}]
    #)
    logger.info(instances[0])
    print('Instance id just created:', iid)
 #   print('Instances in the SSM instances list right now:')
    #i = ec2.Instance(id= iid)
    #print("wait")
    #i.wait_until_running()
    #print("done")


## Run command against your linux VM
def runRemoteShellCommands (InstanceId):
    ssm_client = boto3.client('ssm', region_name=region) 

    ssm_client.client.describe_instance_information()


    response = ssm_client.send_command( InstanceIds=[InstanceId], DocumentName="AWS-RunShellScript", Parameters={'commands':[ 'sudo yum install docker']},)
    command_id = response['Command']['CommandId']
    output = ssm_client.get_command_invocation( CommandId=command_id, InstanceId=InstanceId)
    while output['Status'] == "InProgress":   
        output = ssm_client.get_command_invocation( CommandId=command_id, InstanceId=InstanceId) 
    print(output['StandardOutputContent'])


def StopInstance(instance_id):
    ec2_client = session.client("ec2", region_name="us-east-1")
    response = ec2_client.stop_instances(InstanceIds=[instance_id])
    print(response)

def TerminateInstance(instance_id):
    ec2_client = session.resource("ec2", region_name="us-east-1")
    print(ec2_client.Instance(instance_id).terminate())
    
def GetQueueSize(name):
    #print("Accessing Queue: " + name)
    # Get the service resource
    #  sqs = boto3.resource('sqs', region_name='us-east-1')
    # Get the queue
    sqs = session.resource('sqs',  region_name=region)
    queue = sqs.get_queue_by_name(QueueName=name)
    
    n = queue.attributes.get('ApproximateNumberOfMessages')
    #print("queue approximately has: " + str(n) + " messages")
    return int(n)

def MakeQueue(name):

    sqs = session.resource('sqs',  region_name=region)

    queue = sqs.create_queue(QueueName=name)
        
    print(str(queue) + " created")

def SendQueue(name, data):
    # Create a new message
    sqs = session.resource('sqs',  region_name='us-east-1')
    queue = sqs.get_queue_by_name(QueueName=name)


    response = queue.send_message(MessageBody=data)
    # The response is NOT a resource, but gives you a message ID and MD5
    print(response.get('MessageId'))
  #  print(response.get('MD5OfMessageBody'))
    print("sent: " + data )


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


def MakeFifoQueue(name):

    sqs = session.resource('sqs',  region_name=region)
    queue = sqs.create_queue(QueueName=name, Attributes={'FifoQueue':'true'})
    

    # You can now access identifiers and attributes
    print(queue.url)

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
    l9 = 'echo ' + '"aws_session_token=' + config['sg'] + '" ' +'>> creds.env'
    l10 = 'sudo yum install docker -y'
    l11 = 'sudo service docker start'
    l12 = 'sudo docker pull 1734673/puller'
    l13 = 'sudo docker network create -d bridge myapp_net'

    lines = ["#!/bin/bash",l1,l2,l3,l4,l5,l6,l7,l8,l9,l10,l11,l12, l13]
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

def create_bucket(bucket_name, region=None):
    botoClient.create_bucket(Bucket=bucket_name)
    
#upload borg kube to s3
def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = session.client('s3')
    s3_resource = session.resource('s3')
    #try:
    response = s3_client.upload_file(file_name, bucket, object_name, ExtraArgs={'ACL':'public-read'})
    #s3bucket = s3_resource.
    #key = s3bucket.lookup('BorgKube.py')
    #key.set_acl('public-read')
    print("borgKubeUploaded")
    return True

# create security group
def CreateSecurityGroup(name):
    security_client = session.client('ec2')
    response = security_client.create_security_group(
    Description='BorgSecurityGroup to allow ssh connections',
    GroupName='BorgSecurityGroup',
    VpcId='001',
    TagSpecifications=[
        {
            'ResourceType': 'capacity-reservation'|'client-vpn-endpoint'|'customer-gateway'|'carrier-gateway'|'dedicated-host'|'dhcp-options'|'egress-only-internet-gateway'|'elastic-ip'|'elastic-gpu'|'export-image-task'|'export-instance-task'|'fleet'|'fpga-image'|'host-reservation'|'image'|'import-image-task'|'import-snapshot-task'|'instance'|'instance-event-window'|'internet-gateway'|'ipam'|'ipam-pool'|'ipam-scope'|'ipv4pool-ec2'|'ipv6pool-ec2'|'key-pair'|'launch-template'|'local-gateway'|'local-gateway-route-table'|'local-gateway-virtual-interface'|'local-gateway-virtual-interface-group'|'local-gateway-route-table-vpc-association'|'local-gateway-route-table-virtual-interface-group-association'|'natgateway'|'network-acl'|'network-interface'|'network-insights-analysis'|'network-insights-path'|'network-insights-access-scope'|'network-insights-access-scope-analysis'|'placement-group'|'prefix-list'|'replace-root-volume-task'|'reserved-instances'|'route-table'|'security-group'|'security-group-rule'|'snapshot'|'spot-fleet-request'|'spot-instances-request'|'subnet'|'traffic-mirror-filter'|'traffic-mirror-session'|'traffic-mirror-target'|'transit-gateway'|'transit-gateway-attachment'|'transit-gateway-connect-peer'|'transit-gateway-multicast-domain'|'transit-gateway-route-table'|'volume'|'vpc'|'vpc-endpoint'|'vpc-endpoint-service'|'vpc-peering-connection'|'vpn-connection'|'vpn-gateway'|'vpc-flow-log',
            'Tags': [
                {
                    'Key': 'string',
                    'Value': 'string'
                },
            ]
        },
    ],
    DryRun=True|False
)
create_bucket("borg-kube-bucket2")
upload_file("BorgKube.py", bucket = "borg-kube-bucket2")
CreateInitScripts()



MakeQueue("LaunchedQueue")
MakeFifoQueue("CreatorQueue.fifo")
MakeFifoQueue("InputQueue.fifo")
MakeQueue("InputQueue")
# MakeFifoQueue("CreatorQueueProducer.fifo")
# # orders the creators to make once consumer machine
SendQueueFifo("CreatorQueue.fifo", 1)
MakeFifoQueue("CreatorIntegrity.fifo")
MakeFifoQueue("ResultQueue.fifo")
MakeQueue("ResultQueue")
shellPuller = open('initConsumer.sh')
shellPusher = open('initProducer.sh')
shellCreator = open('initCreator.sh')
shellKube = open("initBorgKube.sh")


# # # launch creator
# # # send commands to creators using the fifo creator queue
LaunchCreator(name = "Creator")
time.sleep(10)
LaunchCreator(name = "Creator2")
time.sleep(10)
LaunchProducer(name = "Producer")


# check size of queue compared to 10s ago
lastQueueSize = 0

# demand the launching of the first borg kube consumer
LaunchBorgKube(name="Kube", n = 1)


time.sleep(30)
# kill kube test
#StopBorgKube()

takenDownConsumer = False
takenDownCreator = False

minLength = 200
maxLength = 800
terminations = 3
terminationTimes = []
terminationChecks = []
#choose three positions to kill a worker
for i in range(0, terminations):
    terminationTimes.append(random.randint(minLength, maxLength))
    terminationChecks.append(False)

#terminationTimes = terminationTimes.sort()
print(str(terminationTimes))
print(str(terminationChecks))


# wait some time because we don't want to start scaling too soon
time.sleep(90)
startTime  = time.time()





while(True):

    # randomly kill a consumer

    currentTime = time.time() - startTime
    for i in range(0, terminations):
        if(currentTime > terminationTimes[i] and terminationChecks[i] == False):
            terminationChecks[i] = True
            StopBorgKube()


    interval = 60
    totalQueueSize = 0
    for i in range(0, interval):
        totalQueueSize += GetQueueSize("InputQueue")
        time.sleep(1)
    currentQueueSize = totalQueueSize / interval
    currentQueueSize = math.floor(currentQueueSize)
    queueSizeRecord = "QUEUE,"
    queueSize = str(currentQueueSize)
    queueSizeRecord = queueSizeRecord + queueSize + "," + str(time.time())

    
    

    SendQueue("ResultQueue", data = queueSizeRecord)
    if(currentQueueSize > lastQueueSize + 40):
        print("LaunchingNewConsumer")
        SendQueueFifo("CreatorQueue.fifo", 1)
    if(currentQueueSize > lastQueueSize + 20):
        print("LaunchingNewConsumer")
        SendQueueFifo("CreatorQueue.fifo", 1)
    elif(currentQueueSize > lastQueueSize):
        print("LaunchingNewConsumer")
        SendQueueFifo("CreatorQueue.fifo", 1)
    elif(currentQueueSize < 10 and lastQueueSize > currentQueueSize):
        print("Stopping Consumers")
        SendQueueFifo("CreatorQueue.fifo", -1)
    elif(currentQueueSize == 0):
        print("Stopping Consumers")
        SendQueueFifo("CreatorQueue.fifo", -1)
    lastQueueSize = currentQueueSize



