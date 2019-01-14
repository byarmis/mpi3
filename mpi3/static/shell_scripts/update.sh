#!/usr/bin/env bash

papirus-write "Updating" --rotation 90
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y
# TODO: Add papirus and pip updates
papirus-write "Update complete" --rotation 90
sleep 3

./reboot.sh
