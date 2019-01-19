#!/usr/bin/env bash

# https://stackoverflow.com/questions/24112727/
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

papirus-write "Updating" --rotation 90
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y
sudo rpi-update
# TODO: Add papirus and pip updates
papirus-write "Update complete" --rotation 90
sleep 3

${parent_path}/reboot.sh
