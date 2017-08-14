#!/bin/python

from mpi3.model.model import Model
from mpi3.view.view import View
from mpi3 import initialize

import logging
import subprocess
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Player(object):
    def __init__(self):
        logger.debug('Initializing player')
        self.config = initialize.get_config()
        self.model = Model(self.config)
        self.view = View(self.config)
        self.volume = self.model.volume

        self.is_playing = False
        self.process = None

        initialize.setup_buttons(self.config,
                                 up=self.up,
                                 down=self.down,
                                 select=self.sel,
                                 play=self.play,
                                 volume=self.vol)

        self.initialize_mpg123()

    def initialize_mpg123(self):
        self.process = subprocess.Popen(['mpg123', '--remote'],
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE)

    def play_next_song(self):
        if self.process.poll():
            logger.debug('Player is not running.  Starting...')
            self.initialize_mpg123()

        logger.debug('Getting next song')
        next_song = self.model.get_next()
        if next_song:
            logger.debug('Next song\'s path is: {}'.format(next_song))
            logger.debug('Playing next song')
            self.play_song(next_song)
            logger.debug('Playing next song started')

    def play_song(self, song_path):
        if self.is_playing:
            logger.debug('Stopping current song')
            self.stop()

        self.process.stdin.write('LOAD {}\n'.format(song_path))
        self.is_playing = True

    def stop(self):
        self.process.stdin.write('STOP\n')
        self.is_playing = False
        logger.debug('Song stopped')

    def up(self, _):
        logger.debug('UP')
        vol = self.volume.increase
        logger.debug('Volume increased to {}'.format(vol))

    def down(self, _):
        logger.debug('DOWN')
        vol = self.volume.decrease
        logger.debug('Volume decreased to {}'.format(vol))

    def sel(self, _):
        logger.debug('SELECT')
        self.stop()

    def play(self, _):
        logger.debug('PLAY')
        self.process.stdin.write('PAUSE\n')
        logger.debug('Song paused')

    def vol(self, _):
        logger.debug('VOL pressed')
        logger.debug('Playing next song')
        self.play_next_song()

    def run(self):
        logger.debug('Running player')

        logger.debug('Playing music started')

        self.play_song(self.model.get_first())
        while self.model.has_songs_in_playlist:
            self.process.wait()
            self.play_next_song()

        logger.debug('Running player-- complete')
