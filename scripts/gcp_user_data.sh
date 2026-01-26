#! /bin/bash
sudo yum update -y
sudo yum install -y docker
sudo yum install -y iperf3
sudo pip3 install requests
sudo pip3 install urllib3==1.26.15
sudo pip3 install openai
sudo service docker start
sudo usermod -a -G docker ec2-user
sudo curl https://igor-prosimo.s3.eu-west-1.amazonaws.com/network_testing.py -o /home/ec2-user/network_testing.py
sudo docker pull iracic82/prosimo-flask-app-labs:latest
sudo docker pull iracic82/prosimo-iperf3:latest
sudo docker pull iracic82/prosimo-postgresql:latest
sudo docker pull iracic82/prosimo-flask-sqlclient:latest
sudo docker pull iracic82/prosimo-security-api:latest
sudo docker run -d -p 5000:5000 iracic82/prosimo-flask-sqlclient:latest
sudo docker run -d -p 5432:5432 iracic82/prosimo-postgresql:latest
sudo docker run -d --name iperf-server -p 5201:5201/tcp -p 5201:5201/udp -p 5201:5201/sctp iracic82/prosimo-iperf3:latest -s
