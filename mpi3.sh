#!/usr/bin/env bash

rm .docker-communication
touch .docker-communication

mkdir --parents /home/pi/Music
mkdir --parents /var/log

pwd="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

sudo docker run \
     --privileged=true \
     -v $pwd/.docker-communication:/docker-communication \
     -v $pwd/mpi3/config.yaml:/config.yaml \
     -v /var/log/mpi3.log:/var/log/mpi3.log \
     -v /home/pi/Music/:/Music/ \
     --device /dev/snd \ 
     byarmis/mpi3

exit-script.sh 

