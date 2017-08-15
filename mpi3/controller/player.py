#!/bin/python

from mpi3.model.model import Model
from mpi3.view.view import View
from mpi3 import initialize

import logging
import subprocess

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Player(object):
    def __init__(self):
        logger.debug('Initializing player')
        self.config = initialize.get_config()
        self.model = Model(self.config)
        self.view = View(self.config)
        self.volume = self.model.volume

        self.button_mode = 'NORMAL'

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

    def change_song(self, forward=True):
        if self.process.poll():
            logger.debug('Player is not running.  Starting...')
            self.initialize_mpg123()

        logger.debug('Getting next song')
        next_song = self.model.get_next() if forward else self.model.get_prev()

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

        if self.button_mode == 'NORMAL':
            pass

        elif self.button_mode == 'VOLUME':
            vol = self.volume.increase
            logger.debug('Volume increased to {}'.format(vol))

        elif self.button_mode == 'PLAYBACK':
            logger.info('Playing next song')
            self.change_song(forward=True)

    def down(self, _):
        logger.debug('DOWN')

        if self.button_mode == 'NORMAL':
            pass

        elif self.button_mode == 'VOLUME':
            vol = self.volume.decrease
            logger.debug('Volume decreased to {}'.format(vol))

        elif self.button_mode == 'PLAYBACK':
            logger.info('Playing previous song')
            self.change_song(forward=False)

    def sel(self, _):
        logger.debug('SELECT')

        if self.button_mode == 'NORMAL':
            pass

        elif self.button_mode in ('VOLUME', 'PLAYBACK'):
            # Pause
            self.is_playing = not self.is_playing
            self.process.stdin.write('PAUSE\n')
            logger.debug('Song paused')

    def play(self, _):
        logger.debug('PLAY')

        if self.button_mode == 'NORMAL':
            self.button_mode = 'PLAYBACK'

        elif self.button_mode == 'VOLUME':
            self.model.next_playback_state()

        elif self.button_mode == 'PLAYBACK':
            self.button_mode = 'NORMAL'

    def vol(self, _):
        logger.debug('VOL pressed')
        if self.button_mode == 'NORMAL':
            pass

        elif self.button_mode == 'VOLUME':
            self.button_mode = 'NORMAL'

        elif self.button_mode == 'PLAYBACK':
            self.model.next_playback_state()

    def run(self):
        logger.debug('Running player')

        logger.debug('Playing music started')

        self.play_song(self.model.get_first())
        while self.model.has_songs_in_playlist:
            self.process.wait()
            self.change_song(forward=True)

        logger.debug('Running player-- complete')
