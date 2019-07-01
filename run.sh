#!/usr/bin/env bash

rm .docker-communication
touch .docker-communication
docker run \
    --privileged=true \
    -v ${pwd}/.docker-communication:/docker-communication \
    -v /home/pi/Music/:/Music/
    byarmis/mpi3

exit-script.sh 

