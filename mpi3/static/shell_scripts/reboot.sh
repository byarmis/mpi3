#!/usr/bin/env bash

papirus-clear
papirus-write "Rebooting" --rotation 90
sleep 2
papirus-clear
papirus-draw ../imgs/restart.png -t resize -r 90

sudo reboot
