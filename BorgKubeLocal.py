import os
import time
import boto3
import fabric
""" :type : pyboto3.s3 """
import docker
from dotenv import dotenv_values
import threading
import string
import random
import psutil
config = dotenv_values("creds.env")
dockerClient = docker.from_env()
hostCpuUsage = 0
## if on local
##config = dotenv_values("creds.env")
region = config['region']
hostname = "localhost"
session = boto3.Session(
    aws_access_key_id=config['aws_access_key_id'],
    aws_secret_access_key=config['aws_secret_access_key'],
    aws_session_token= config['aws_session_token']
)

localBuffer = []
localBufferMaxSize = 300
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

def SendDroneCreated():
    record = ""
    # format the data
    dataType = "DRONE,CREATED,"
    record = record + dataType
    record = record + str(time.time())
    sendToEndpoint(record)
def SendDroneKilled():
    record = ""
    # format the data
    dataType = "DRONE,DESTROYED,"
    record = record + dataType
    record = record + str(time.time())
    sendToEndpoint(record)
# take an array of cpu 
def SendCpuDiagnostic(data):
    record = ""
    # format the data
    dataType = "CPU,"
    record = record + dataType
    for item in data:
        cpuStat = str(item) + ","
        record = record + cpuStat
    record = record + str(time.time())

    print("CPU DIAGNOSTIC: " + record)
    sendToEndpoint(record)
    


def sendToEndpoint(data):
    # Create a new message
    
    sqs = session.resource('sqs',  region_name='us-east-1')
    queue = sqs.get_queue_by_name(QueueName="ResultQueue")

    response = queue.send_message(MessageBody=data)
    # The response is NOT a resource, but gives you a message ID and MD5
    print(response.get('MessageId'))
  #  print(response.get('MD5OfMessageBody'))
    print("sent: " + data )



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

client = docker.from_env()

drones = []
maxDrones = 7
mayEditDrones = True
dronecount = 0
def id_generator(size=6, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def CreateDroneToList(sendReport):
    global mayEditDrones
    global client
    global maxDrones
    global dronecount
    mayEditDrones = False
    
    
    i = 1
    numberList =[]
    for drone in drones:
        numberList.append(drone.name[0])
    namingInconsistencies = True
    while(namingInconsistencies):
        if(numberList.count(str(i))>0):
            i+=1
        if(i>maxDrones):
            break
        if(numberList.count(str(i)) == 0):
            namingInconsistencies = False


    number = str(i)
    droneName = number + "-of-" + str(maxDrones) + id_generator()
    
    if(namingInconsistencies == False):
        if(sendReport):
            SendDroneCreated()
        container = client.containers.run(
            image='1734673/puller',
            stdin_open=True,
            name = droneName,
            hostname = droneName,
            tty=True,
            volumes=['D:/Big Data/TestStream/DockerImages/Docker_1/docker_assignment/aws:/aws'],
            detach = True,
            publish_all_ports = True,
            network = "myapp_net",
            command="python BorgDrone.py & python BorgDrone.py"
        )
        drones.append(container)
        dronecount += 1
        mayEditDrones = True
        print("Created Drone")
    


        
def KillDrone(drone):
    global dronecount
    drone.remove(v = False, link = False, force = True)
    dronecount -= 1
    SendDroneKilled()
    #client.containers.get(drone.id).remove()

def calculate_cpu_percent(d):
    cpu_count = len(d["cpu_stats"]["cpu_usage"]["percpu_usage"])
    cpu_percent = 0.0
    cpu_delta = float(d["cpu_stats"]["cpu_usage"]["total_usage"]) - \
                float(d["precpu_stats"]["cpu_usage"]["total_usage"])
    system_delta = float(d["cpu_stats"]["system_cpu_usage"]) - \
                   float(d["precpu_stats"]["system_cpu_usage"])
    if system_delta > 0.0:
        cpu_percent = cpu_delta / system_delta * 100.0 * cpu_count
    return cpu_percent

def pollCpusForMean(samples, duration):
    total_cpu_percent = 0
    interval = float(duration) / float(samples)
   # print("interval: " + str(interval))
    total_mean_cpu_percent = 0

    # first, poll for our cpu usage
    hostCpuUsage = float(psutil.cpu_percent(4))
    print('The host CPU usage is: ', str(hostCpuUsage))

    # initialise list
    cpuUsageList = []
    cpuUsageList.append(hostCpuUsage)
    for i in range (0, len(drones)):
        cpuUsageList.append(0.0)


    for j in range (0, samples):
        mean_cpu_percent = 0
        for i in range (0, len(drones)):
            # status = drones[i].stats(decode=None, stream = False)
            try:
                stats = drones[i].stats(stream=False)
                cpuPercent = calculate_cpu_percent(stats)
                total_cpu_percent += cpuPercent
                print(drones[i].name + " cpu at " + str(cpuPercent))
                cpuUsageList[i+1] += cpuPercent/samples
            except:
                print("drone is down")
                drones.remove(drones[i])
                if(len(drones) < 1):
                    CreateDroneToList(True)
            mean_cpu_percent = (total_cpu_percent / len(drones))


        total_mean_cpu_percent += mean_cpu_percent
        #time.sleep(interval)
    
    ## now send this data for diagnostics
    SendCpuDiagnostic(cpuUsageList)
    return (total_cpu_percent / samples)/len(drones)

def DronePopulationControlLoop():
    global mayEditDrones
    mean_cpu_percent = 0
    total_cpu_percent = 0
    minimum_cpu_percent = 60
    max_cpu_percent = 80
    time.sleep(10)
    while (True):
        time.sleep(1)
        if(len(drones) > 0):
            
            mean_cpu_percent = pollCpusForMean(3, 3)
            print("Mean CPU percent at: -----" + str(mean_cpu_percent) + "-----")

        # if the docker drones/containers are slacking, kill one
        if(mean_cpu_percent < minimum_cpu_percent and len(drones) > 1):
            # kill drone and remove it after 2s
            mayEditDrones = False
            condemnedDrone = drones[len(drones) -1]
            drones.remove(condemnedDrone)
            print("killing drone: " + str(condemnedDrone))
            KillDrone(condemnedDrone)
            mayEditDrones = True
        
        # if the docker drones/containers are maxing out, we require a new one
        if(mean_cpu_percent > max_cpu_percent and mayEditDrones and len(drones) < maxDrones and hostCpuUsage < 100 and mayEditDrones):
            print("creating new drone")
            mayEditDrones = False
            
            CreateDroneToList(True)


        

def KubeInitialisation():
    global client
    broker = client.containers.run(
        image='rabbitmq:3-management',
        hostname = 'rabbitmqhost',
        name =  'rabbitmq',
        stdin_open=True,
        tty=True,
        volumes=['D:/Big Data/TestStream/DockerImages/Docker_1/docker_assignment/aws:/aws'],
        detach = True,
        ports = {15672:15672, 5672:5672},
        network = "myapp_net"
    )
    print("Created broker")
    CreateDroneToList(True)

    phaser = client.containers.run(
        image='1734673/puller',
        name = 'phaser',
        stdin_open=True,
        tty=True,
        volumes=['D:/Big Data/TestStream/DockerImages/Docker_1/docker_assignment/aws:/aws'],
        detach = True,
        publish_all_ports = True,
        network = "myapp_net",
        command="python BorgPhaser.py"
    )
    print("created phaser")

    vinculum = client.containers.run(
        image='1734673/puller',
        name = 'vinculum',
        stdin_open=True,
        tty=True,
        volumes=['D:/Big Data/TestStream/DockerImages/Docker_1/docker_assignment/aws:/aws'],
        detach = True,
        publish_all_ports = True,
        network = "myapp_net",
        command="python BorgVinculumLocal.py"
    )
    print("Created vinculum")
    time.sleep(5)
    

KubeInitialisation()
DronePopulationControlLoop()





#dockerClient.containers.run("1734673/puller", detach=True, command="python botoPusher.py", )
# while (True):
#     if(localBuffer.count < localBufferMaxSize):
#         UpdateLocalBuffer("LaunchedQueue")
    