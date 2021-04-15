#!/bin/bash

cd "$(dirname "$0")"
cwd=`pwd`

while true
do
cd ${cwd}
timedatectl set-timezone UTC
service dump1090-fa restart
sleep 1
cd build/receiver
./receiver.py
sleep 10
done

