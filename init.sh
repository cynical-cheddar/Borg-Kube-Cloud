#!/bin/bash
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1
echo BEGIN
sudo mkdir aws
cd aws
echo "region=us-east-1" > creds.env
echo "aws_access_key_id=ASIA2UTLWGM7KLP6XXWH" >> creds.env
echo "aws_secret_access_key=/rklHMCsa2IKsXW+2rwWwLf9HaPCgiwWpb9k7lza" >> creds.env
echo "aws_session_token=FwoGZXIvYXdzEOz//////////wEaDCLiUUz80yo2veXsDSLGAQoR7Z024vfHnbZJeQeCNFpXg8M+VFP/knpxcSK6WkMBGVPT5MQajldF68nF679Pi6lC4qIoJHv0pya/wSSNmR7oqB2bfOTMqfdlVOmT4F2L8nEw+TVxm2xriJ1HTwmfLv2Z506/7XH6OR5E85iHSCcCe5pANM07mmvL8NHi5uqyyn6p1bVxkMosW/lJPpdQLKjFNCW9KVz2PeJSGYyO2VE75FbTiLrs+poWoADeLL4QwNY6E0C/8f8eLAPKTrPbG6PiHXkugCi0iIiNBjIt7qZLsqgg9Bj+HG3DJpfqNBM1fdeY7qPl/RGPHpW1McfpqsSLjFebbMSEGIKh" >> creds.env




sudo yum install docker -y
sudo service docker start
sudo docker pull 1734673/puller
sudo docker run -ip 3000:3000 -v "/aws:/aws" 1734673/puller sh -c "python botoPuller.py >>  logfile.txt"


#cat <<EOF >/creds.env
#aws_access_key_id=ASIA2UTLWGM7NGRO6V4H
#aws_secret_access_key=OXRD+oxYX+gHcC7wveL+3zmf1gFDCFYa1zriVXD5
#aws_session_token=FwoGZXIvYXdzENn//////////wEaDDPHZeHrWDiVx0ye9CLGASHMYc4NQSTA80hbcViLc/kTZ57ACA2oELYD6bpN6g+FNpp8/hBwzF9yZqOh8XlbTh20appKqe9nre7JGZstJU+ehexovWqNRsxHdpe1knM7eJT9kYJQ02PGytM0LdGtfT4mYJld8V77kgpmKf7E7VCddC56QTJfVu+IEIDE66bVE56KkgL6iyRme4CVttw6UKTsdKyq9hO/dIEtpbzKW3/QZ45g8/TxL5gAr6iNe/HZ/7rWhNytvgyYRDxwzTb6ARtxCibAMiik74ONBjIttHbkkW5erYpYPdmvr9yvfCDZzYfada75nEozNMAxsrkcnP61uHSUqjkJITFP
#region = us-east-1




echo END