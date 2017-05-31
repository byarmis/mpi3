#!/bin/python3
import pyaml

# def get_constants():
#     return {
#         'font_size': 15,
#         'title_size': 13,
#         'screen_size': {'height': 200,
#                         'width': 96},
#         'colors': {'white': 1, 'black': 0}
#     }
#

def get_config():
    with open('config.yaml') as f:
        c = pyaml.load(f)

    c['page_size'] = (c['screen_size']['height'] - c['font']['title_size']) // c['font']['size']
    return c
