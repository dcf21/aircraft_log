#!/bin/bash

cd "$(dirname "$0")"
cwd=`pwd`

while 1
do
cd ${cwd}
timedatectl set-timezone UTC
service dump1090-fa restart
cd build/receiver
./receiver.py
sleep 10
done

