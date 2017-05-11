#!/usr/bin/env python

import yaml

with open('example.yaml') as f:
    y = yaml.safe_load(f)

print y
