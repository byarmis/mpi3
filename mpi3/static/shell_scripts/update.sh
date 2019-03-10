#!/usr/bin/env bash

papirus-write "Updating: Linux" --rotation 90
sudo apt-get update
papirus-write "Updating: Linux Install" --rotation 90
sudo apt-get upgrade -y
papirus-write "Updating: Linux Autoremove" --rotation 90 --fsize 15
sudo apt-get autoremove -y

papirus-write "Updating: Python Packages" --rotation 90
pip3 install -r requirements.txt --upgrade --user

papirus-write "Updating: PaPiRus" --rotation 90
cd $HOME_DIR_papirus
git checkout master
git pull origin master
sudo python3 setup.py install

papirus-write "Update complete" --rotation 90
sleep 3

$HOME_DIR_mpi3/mpi3/static/shell_scripts/reboot.sh
