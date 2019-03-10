#!/usr/bin/env bash

# https://stackoverflow.com/questions/24112727/
papirus-write "Powering down" --rotation 90 --fsize 16
sleep 1
papirus-draw $HOME_DIR_mpi3/mpi3/static/imgs/sleeping.bmp --type resize --rotation 90

sudo poweroff
