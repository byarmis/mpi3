#!/bin/python

import os
import logging
from subprocess import call
from mpi3.model.db import Database

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Volume(object):
    def __init__(self):
        logger.debug('Initializing volume object')
        self.val = 2
        self.set_volume(self.val)

    @property
    def increase(self):
        if self.val < 19:
            self.val += 1
        self.set_volume(self.val)
        return self.get

    @property
    def decrease(self):
        if self.val > 1:
            self.val -= 1
        self.set_volume(self.val)
        return self.get

    @property
    def get(self):
        return self.val * 5

    def set_volume(self, val):
        self.val = val
        call(['amixer', 'sset', 'Master', '{}%'.format(self.get)])


class Library(object):
    def __init__(self, music_config):
        logger.debug('Initializing the library')
        self.db = Database(music_config)


class Model(object):
    def __init__(self, config):
        self.library = Library(config['music'])
        self.volume = Volume()
