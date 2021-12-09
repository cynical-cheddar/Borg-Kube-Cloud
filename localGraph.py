import json
import math
from os import cpu_count
import sys
import time
import numpy as np
from matplotlib import pyplot as plt
import boto3

import logging

import pika
from fabric import task
import requests


from dotenv import dotenv_values

maxSendDuration = 2400
sendInterval1 = 40
sendBoundary1 = 0

sendInterval2 = 20
sendBoundary2 = 120

sendInterval3 = 5
sendBoundary3 = 240

sendInterval4 = 1
sendBoundary4 = 360

sendInterval5 = 0.5
sendBoundary5 = 480

sendInterval6 = 0.2
sendBoundary6 = 600

sendInterval7 = 0.1
sendBoundary7 = 720

sendInterval8 = 0.2
sendBoundary8 = 840

sendInterval9 = 5
sendBoundary9 = 960

sendInterval10 = 20
sendBoundary10 = 660

sendInterval11 = 40
sendBoundary11 = 780

rates = []
times = []
for i in range(1,900):
    times.append(float(i))

    waitTime = 0
    if(i > sendBoundary1):
        waitTime = sendInterval1
    if(i > sendBoundary2):
        waitTime = sendInterval2
    if(i > sendBoundary3):
        waitTime = sendInterval3
    if(i > sendBoundary4):
        waitTime = sendInterval4
    if(i > sendBoundary5):
        waitTime = sendInterval5
    if(i > sendBoundary6):
        waitTime = sendInterval6
    if(i > sendBoundary7):
        waitTime = sendInterval7
    if(i > sendBoundary8):
        waitTime = sendInterval8
    if(i > sendBoundary9):
        waitTime = sendInterval9
    if(i > sendBoundary10):
        waitTime = sendInterval10
    if(i > sendBoundary11):
        waitTime = sendInterval11

    rate = float(1.0/waitTime)*2

    rates.append(rate)

plt.plot(times, rates)
plt.xlabel('Transmission Time / (s)')
plt.ylabel('Send Rate / (Hz)')
plt.title('Variable Request Transmission Rate Over Time')
plt.show()
    
            
