#!/usr/bin/env bash

papirus-write "Updating" --rotation 90
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y
papirus-write "Update complete" --rotation 90
sleep 3

