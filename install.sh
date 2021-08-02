#!/bin/bash

pip3 install peewee
cp parkomat-agent.service /etc/systemd/system/parkomat-agent.service
systemctl enable parkomat-agent
systemctl start parkomat-agent
