#!/bin/bash

pip3 install peewee
cp monitoring.service /etc/systemd/system/monitoring.service
systemctl enable monitoring
systemctl start monitoring
