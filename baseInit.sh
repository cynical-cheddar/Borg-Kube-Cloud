#!/bin/bash
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1
echo BEGIN
sudo mkdir aws
cd aws
echo "region=us-east-1" > creds.env
echo "aws_access_key_id=ASIA2UTLWGM7CFAVQQW4" >> creds.env
echo "aws_secret_access_key=icgvgvsnVboqVxXT5dGfiEA/vPuJUvtYxgtArU3S" >> creds.env
echo "aws_session_token=FwoGZXIvYXdzEAgaDLOR0vnzBYn15h7rxiLGAZFhxbAkXWjpRuQcVzGCs+lwMU7O2N/c2dx6CbRZiz0EuV3kla8+YxqoPJZesUag5ANkb0/OKhFGmS3zSZafSQKkCHVDjdm5b5P6X5JlD2Ob0btqGGxy3vnXCHNpY/THM/WGTtPQXSok4G8fI4568MsU+3yDcFp9xiS291i1xvK6iv7GvkR8zXCD7uGUrPE7xMeW770Zu7mJh07X0m1xMmPcgsij/GjxFuIQJ0gcvZ9gFrEx89MZdLr5N4lhZ+ngqYxQ9HsHjCiXr46NBjItFYXjf0KW2z8kPpePihWStbEQTJPQ1/rf/mX74SnvSJ3byzOCaWA4nRyW2aAN" >> creds.env
sudo yum install docker -y
sudo service docker start
sudo docker pull 1734673/puller
