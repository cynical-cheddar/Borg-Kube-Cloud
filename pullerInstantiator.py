import json
import math
import sys
import time

import boto3

import paramiko

import logging

import pika
from fabric import task
import requests

from dotenv import dotenv_values

## local:
shell = open('initConsumer.sh')
config = dotenv_values("creds.env")
## remote
#config = dotenv_values("aws/creds.env")
region = config['region']

session = boto3.Session(
    aws_access_key_id=config['aws_access_key_id'],
    aws_secret_access_key=config['aws_secret_access_key'],
    aws_session_token= config['aws_session_token']
)

def LaunchNumberedEC2(name):
    LaunchEC2(name+str(GetAmountOfInstances()))

##
def LaunchEC2Mk2():
    ec2r = boto3.resource('ec2' )
    userdata = """#cloud-config
        runcmd:
        - yum install -y docker
    """ % region   

    ssm = True
    ami = 'ami-02e136e904f3da870'
    if ssm == True:
        instance = ec2r.create_instances( ImageId=ami, MinCount=1, MaxCount=1, KeyName='vockey', InstanceType='t2.micro', 
            NetworkInterfaces=[{
            'DeviceIndex': 0,
            'AssociatePublicIpAddress': False
           # 'SubnetId': mySub,
           # 'Groups': secGroupList,
           # 'AssociatePublicIpAddress': AssociatePublicIpAddress
        }],
            Monitoring={ 'Enabled': False },

            UserData=userdata,
            EbsOptimized=False
        )
 ##   

def LaunchEC2(name='COMSM0072_boto_lab', securitygroup=None):
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
        SecurityGroupIds=['sg-0e7ab23f5450fd75c'],
        KeyName='educate-us-east-second',
        UserData = shell.read()
    )
    iid = instances[0].id

    # give the instance a tag name
    ec2.create_tags(
        Resources=[iid],
        Tags=[{'Key': 'Name', 'Value': name}]
    )

    logger.info(instances[0])


    print('Instance id just created:', iid)
    
 #   print('Instances in the SSM instances list right now:')


    i = ec2.Instance(id= iid)
    print("wait")
    i.wait_until_running()
    print("done")

  #  k = paramiko.RSAKey.from_private_key_file("educate-us-east-second.pem")
  #  c = paramiko.SSHClient()
  #  c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  #  print ("\nConnecting to shell using ssh")
  #  c.connect( hostname = i.public_dns_name, username = "ec2-user", pkey = k )
  #  time.sleep(10)
  #  print ("\nExecuting commands on EC2 instance\n")
  #  c.exec_command("sudo yum install docker")
  #  c.exec_command("y")
  #  print ("execution should be done")

    
   # runRemoteShellCommands(iid)





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

LaunchEC2("test")

