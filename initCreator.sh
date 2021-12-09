#!/bin/bash
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1
echo BEGIN
sudo mkdir aws
cd aws
echo "region=us-east-1" > creds.env
echo "aws_access_key_id=ASIAYQIJ55GAEHTWTT6W" >> creds.env
echo "aws_secret_access_key=M7AzS432xYoaxO1IMK8DkfxyYr29WUIlfy/HmH/i" >> creds.env
echo "aws_session_token=FwoGZXIvYXdzEBgaDAAJg6qsSudzgZv/wCK+ARzbbSW/gmuDkKTiiJ/xBPZ+QciTg6uTO0dydCULGkjhTq6IODc3QOExofKjjxnbmAoIpmElM5OH9jE1EHOqgW0ATWfUixVYA1e2aLgZyUdz51bQI0G2MhNF4afJAaLHVxHvvkuadC3iXyAos8FR2MLqw8q4xmc0lWKpXuGSZi92s2N9t1aVsJ89/t0Vq3vraJkxUujioJcDfY5m0GR5uLsdKQnTqSvrWyDSABEtJi2NyrD36OjGAPHrOf1Mn8oo847KjQYyLS/swLd3ZaIw34b6fTAGi61QGWWOVvBQITQLFcfz5nlf8fA8GFcfnOwp/qigDQ==" >> creds.env
echo "aws_session_token=sg-00d9b360167588bb2" >> creds.env
sudo yum install docker -y
sudo service docker start
sudo docker pull 1734673/puller
sudo docker network create -d bridge myapp_net
sudo docker run -ip 3000:3000 -v "/aws:/aws" 1734673/puller sh -c "python botoCreator.py >>  logfile.txt "
echo END