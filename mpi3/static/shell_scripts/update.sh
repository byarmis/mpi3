#!/usr/bin/env bash

papirus-write "Updating" -rot 90
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y
papirus-write "Update complete" -rot 90
sleep 3

