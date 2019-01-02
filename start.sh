#!/bin/bash

pipe1=/tmp/server_in.pipe
pipe2=/tmp/server_out.pipe

if [[ ! -p $pipe1 ]]; then
    mkfifo $pipe1
fi

if [[ ! -p $pipe2 ]]; then
    mkfifo $pipe2
fi

python /home/pi/project/ble_server.py &

/home/pi/project/src/rpi/mpu_test &