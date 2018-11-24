#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from subprocess import run, PIPE
from papirus import PapirusTextPos
from mpi3.__version__ import __version__ as mpi3_ver
from papirus import __version__ as papirus_ver

linux_ver = run(['cat', '/etc/os-release'],
                stdout=PIPE).stdout.decode('utf-8')
REGEX = r'PRETTY_NAME="(.*)"'
linux_ver = re.search(REGEX, linux_ver).group(1)

python_ver = run(['python3', '--version'],
                 stdout=PIPE).stdout.decode('utf-8')

text = PapirusTextPos(rotation=90)
text.AddText('{linux_ver}\n\n{python_ver}\nPapirus:\n{papirus_ver}\n\nMPi3:\n{mpi3_ver}'.format(**locals()),
             size=15)
