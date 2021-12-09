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

import platform    # For getting the operating system name
import subprocess  # For executing a shell command

def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower()=='windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]

    return subprocess.call(command) == 0



while (True):
   # time.sleep(1)
   # print("waiting")
    time.sleep(3)
   # GetQueue("LaunchedQueue")
    ping("google.com")