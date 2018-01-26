#!/bin/python


def get_color(config, black=False, white=False):
    if black:
        return config['colors']['black']
    elif white:
        return config['colors']['white']
    else:
        raise ValueError('Pick either black or white')


def get_screen_size(config):
    return config['screen_size']['width'], config['screen_size']['height']



class RenderHelper(object):
    def __init__(self, config, draw, font, tfont):
        self.draw = draw
        self.font = font
        self.config = config
        self.tfont = tfont

    def get_black(self):
        return get_color(self.config, black=True)
