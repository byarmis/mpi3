#!/bin/python

import logging
from mpi3 import initialize
from subprocess import call

logger = logging.getLogger(__name__)


class Volume(object):
    def __init__(self):
        logger.debug('Initializing volume object')
        self.val = 1
        self.set_volume(self.val)

    @property
    def increase(self):
        if self.val < 19:
            self.val += 1
        self.set_volume(self.val)
        logger.debug('Volume now {}'.format(self.get))
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
        logger.debug('Setting volume to be {}'.format(self.get))
        call(['amixer', 'sset', 'Master', '{}%'.format(self.get)])


class Model(object):
    def __init__(self, config):
        self.files = initialize.scan_libraries(config['music']['directory'])
        self.volume = Volume()
