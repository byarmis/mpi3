#!/usr/bin/env bash

# https://stackoverflow.com/questions/24112727/
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"
cd ..

papirus-clear
papirus-draw ./imgs/sleeping.bmp -t resize -r 90
sleep 1

sudo poweroff
