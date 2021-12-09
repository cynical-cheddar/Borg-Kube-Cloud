# Dockerfile, Image, Container
FROM python:3.8
ADD botoPuller.py .
ADD botoPullerLocal.py .
ADD botoPusher.py .
ADD botoCreator.py .
ADD BorgKube.py .
ADD BorgKubeLocal.py .
ADD BorgDrone.py .
ADD BorgVinculum.py .
ADD BorgVinculumLocal.py .
ADD BorgPhaser.py .
ADD BorgDroneRemote.py .
RUN pip install boto3 pika fabric requests python-dotenv botocore docker psutil