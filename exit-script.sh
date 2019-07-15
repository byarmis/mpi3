#!/usr/bin/env bash

if [ -s "$.docker-communication" ]
then
    sh ./mpi3/static/shell_scripts/$(cat .docker-communication).sh
fi

