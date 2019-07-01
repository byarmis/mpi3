#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from subprocess import run, PIPE
from time import sleep

from papirus import PapirusTextPos
from mpi3.__version__ import __version__ as mpi3_ver
from papirus import __version__ as papirus_ver

linux_ver_raw = run(['cat', '/etc/os-release'],
                    stdout=PIPE).stdout.decode('utf-8')
linux_ver = re.search(r'PRETTY_NAME="(.*)"', linux_ver_raw).group(1)

python_ver = run(['python3', '--version'],
                 stdout=PIPE).stdout.decode('utf-8')

text = PapirusTextPos(rotation=90)

text.AddText(f'{linux_ver}\n\n{python_ver}\nPapirus:\n{papirus_ver}\n\nMPi3:\n{mpi3_ver}', size=15)

sleep(3)

