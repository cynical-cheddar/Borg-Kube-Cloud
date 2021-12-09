import boto3
from dotenv import dotenv_values
instanceMessageDeduplicationId = 0

config = dotenv_values("creds.env")
## remote
#config = dotenv_values("aws/creds.env")
region = config['region']

session = boto3.Session(
    aws_access_key_id=config['aws_access_key_id'],
    aws_secret_access_key=config['aws_secret_access_key'],
    aws_session_token= config['aws_session_token']
)


name = 'educate-us-east-second'
ec2 = session.client('ec2', region)
response = ec2.create_key_pair(KeyName=name)

private_key_file=open(name,"w")
private_key_file.write(response['KeyMaterial'])
private_key_file.close