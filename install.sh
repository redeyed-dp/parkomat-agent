#!/bin/bash

pip3 install peewee
cp parkomat-agent.service /etc/systemd/system/parkomat-agent.service
systemctl enable parkomat-agent
systemctl start parkomat-agent

echo '0 3 * * * cd /opt/parkomat-agent && ./update.sh' >> /var/spool/cron/crontabs/root
