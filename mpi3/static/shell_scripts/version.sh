#!/usr/bin/env bash

linux_ver=echo 'Linux: ' $(cat /etc/os-release | grep PRETTY_NAME | cut --delimiter \" --fields 2)
python_ver=$(python3 --version)
mpi3_ver=echo 'MPi3: ' $(mpi3 --version)
papirus_ver=echo 'Papirus: ' $(papirus --version)

to_write=echo -e '$linux_ver\n$pyton_ver\n$papirus_ver\n$mpi3_ver'

papirus-write $to_write -rot 90
unset linux_ver
unset python_ver
unset mpi3_ver
unset papirus_ver
unset to_write
sleep 3

