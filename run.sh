#!/usr/bin/env bash

touch docker-communication
docker pull byarmis/mpi3:latest # change tag?
docker run \
    --privileged=true \
    -v ${pwd}/docker-communication:/docker-communication \
    -v /home/pi/Music/:/Music/
    byarmis/mpi3

exit-script.sh docker-communication

