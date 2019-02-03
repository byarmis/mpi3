#!/usr/bin/env bash

# https://stackoverflow.com/questions/24112727/
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"
cd ..

papirus-write "Rebooting" --rotation 90 --fsize 16
sleep 1
papirus-draw ./imgs/restart.bmp --type resize --rotation 90

sudo reboot
