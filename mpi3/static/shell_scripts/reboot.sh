#!/usr/bin/env bash

# https://stackoverflow.com/questions/24112727/
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"
cd ..

papirus-write "Rebooting" --rotation 90
sleep 2
papirus-draw ./imgs/restart.bmp -t resize -r 90

sudo reboot
