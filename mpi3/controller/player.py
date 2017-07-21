#!/bin/python

from mpi3.model.model import Model
from mpi3.view.view import View
from mpi3 import initialize

import logging
import subprocess
import time

logger = logging.getLogger(__name__)


class Player(object):
    def __init__(self):
        logger.debug('Initializing player')
        self.config = initialize.get_config()
        self.model = Model(self.config)
        self.view = View(self.config)

        initialize.setup_buttons(self.config,
                                 up=self.up,
                                 down=self.down,
                                 select=self.sel,
                                 play=self.play,
                                 volume=self.vol)

        self.process = subprocess.Popen(['mpg123', '--remote'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def up(self, _):
        logger.debug('UP')
        vol = self.model.volume.increase
        logger.debug('Volume increased to {}'.format(vol))

    def down(self, _):
        logger.debug('DOWN')
        vol = self.model.volume.decrease
        logger.debug('Volume decreased to {}'.format(vol))

    def sel(self, _):
        logger.debug('SELECT')
        self.process.stdin.write('STOP\n')

    def play(self, _):
        logger.debug('PLAY')
        self.process.stdin.write('PAUSE\n')

    def vol(self, _):
        logger.debug('volume')

    def run(self):
        logger.debug('Running player')
        self.process.stdin.write('LOAD /home/pi/Music/R.mp3\n')
        logger.debug('Playing music started')

        self.process.wait()

        logger.debug('Running player-- complete')
