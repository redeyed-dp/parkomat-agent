#!/bin/bash

OLD=`git rev-parse --short HEAD`
git pull
NEW=`git rev-parse --short HEAD`
if [[ "$NEW" == "$OLD" ]];
then
    systemctl restart parkomat-agent
fi
