#!/bin/python3
import yaml


def get_config():
    with open('config.yaml') as f:
        c = yaml.load(f)

    c['computed'] = {}
    c['computed']['page_size'] = (c['screen_size']['height'] - c['font']['title_size']) // c['font']['size']
    return c


def scan_library(loc):
    print(f'Scanning {loc}')
    print('Just kidding, this is a test')
