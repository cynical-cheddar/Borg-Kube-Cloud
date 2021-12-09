# CCBD-Coursework
 
Setup Instructions:

Sign into an AWS student lab account.
Copy the aws credentials (excluding [default]):
 aws_access_key_xxxxxxxxxx
 aws_secret_access_xxxxxxxxxx
 aws_session_token=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
 
 Paste the credentials into both creds.env files (one in repo root, one in /aws directory)


Navigate to EC2 from the dashboard.

Add a new security group with the follwing settings:
 INBOUND TRAFFIC - ALL TCP - ANYWHERE IPV4
 INBOUND TRAFFIC - SSH - PORT 22
 OUTBOUND TRAFFIC - ALL
 
 copy the security group id
 
 write the line 'sg=*security-group-id* to both creds.env files, where security-group-id is the id you just copied. Do not include any asterisks.
 

Create a new Key Pair:
 Name it educate-us-east-second
 
 -----------------------------------------
 
 Terminate all EC2s and purge all SQS queues before running tests
 
 Launch architecture tests by running statusMonitor.py in one terminal, and endpoint.py --EC2 in another

 Launch Borg Kube tests by running BorgKubeLocal.py in one terminal, and endpoint.py --Kube in another

