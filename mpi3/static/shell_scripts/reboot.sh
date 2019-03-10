#!/usr/bin/env bash

papirus-write "Rebooting" --rotation 90 --fsize 16
sleep 1
papirus-draw $HOME_DIR_mpi3/mpi3/static/imgs/restart.bmp --type resize --rotation 90

sudo reboot
