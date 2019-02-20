#!/usr/bin/env bash

# https://stackoverflow.com/questions/24112727/
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"
cd .. # static
cd .. # mpi3
cd .. # root dir

papirus-write "Updating: Linux" --rotation 90
sudo apt-get update
papirus-write "Updating: Linux Install" --rotation 90
sudo apt-get upgrade -y
papirus-write "Updating: Linux Autoremove" --rotation 90 --fsize 15
sudo apt-get autoremove -y

papirus-write "Updating: Python Packages" --rotation 90
pip3 install -r requirements.txt --upgrade --user

papirus-write "Updating: PaPiRus" --rotation 90
cd ../PaPiRus
git checkout master
git pull origin master
sudo python3 setup.py install

papirus-write "Update complete" --rotation 90
sleep 3

${parent_path}/reboot.sh
