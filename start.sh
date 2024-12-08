#!/usr/bin/bash

# This script is used to start the freeradius application in the container
service freeradius start
status=$(service freeradius status)
# if the return string contains "active (running)" then the service is running
if [[ $status == *"is running"* ]]; then
    echo "Freeradius service is running"
else
    echo "Freeradius service is not running: $status"
    exit 1
fi

exec tail -f /dev/null
