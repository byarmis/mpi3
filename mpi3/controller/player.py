#!/bin/python

import logging
import subprocess

from mpi3 import initialize
from mpi3.model.model import Model
from mpi3.view.view import View
from mpi3.model.constants import (DIRECTION as DIR,
                                  BUTTON_MODE as MODE)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Player(object):
    def __init__(self):
        logger.debug('Initializing player')
        self.config = initialize.get_config()
        self.model = Model(self.config)
        self.view = View(self.config)
        self.volume = self.model.volume

        self.button_mode = MODE.NORMAL

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

    def change_song(self, direction):
        if self.process.poll():
            logger.debug('Player is not running.  Starting...')
            self.initialize_mpg123()

        logger.debug('Getting next song')
        next_song = self.model.get_next_song(direction)

        if next_song:
            logger.debug("Next song's path is: {}".format(next_song))
            logger.debug('Playing next song')
            self.play_song(next_song)
            logger.debug('Playing next song started')

        else:
            logger.debug("There isn't a next song to play.  Stopping")
            self.stop()

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

        if self.button_mode == MODE.NORMAL:
            pass

        elif self.button_mode == MODE.VOLUME:
            vol = self.volume.increase
            logger.debug('Volume increased to {}'.format(vol))

        elif self.button_mode == MODE.PLAYBACK:
            logger.info('Playing next song')
            self.change_song(direction=DIR.FORWARD)

    def down(self, _):
        logger.debug('DOWN')

        if self.button_mode == MODE.NORMAL:
            logger.debug('Mode is NORMAL')
            pass

        elif self.button_mode == MODE.VOLUME:
            logger.debug('Decreasing volume')
            vol = self.volume.decrease
            logger.debug('Volume decreased to {}'.format(vol))

        elif self.button_mode == MODE.PLAYBACK:
            logger.info('Playing previous song')
            self.change_song(direction=DIR.BACKWARD)

    def sel(self, _):
        logger.debug('SELECT')

        if self.button_mode == MODE.NORMAL:
            pass

        elif self.button_mode in (MODE.VOLUME, MODE.PLAYBACK):
            # Pause
            self.is_playing = not self.is_playing
            self.process.stdin.write('PAUSE\n')
            logger.debug('Song paused')

    def play(self, _):
        logger.debug('PLAY')

        if self.button_mode == MODE.NORMAL:
            logger.debug('Changing button mode to PLAYBACK')
            self.button_mode = MODE.PLAYBACK

        elif self.button_mode == MODE.VOLUME:
            logger.debug('Getting next playback mode')
            self.model.next_playback_state()

        elif self.button_mode == MODE.PLAYBACK:
            logger.debug('Exiting PLAYBACK button mode, going back to NORMAL')
            self.button_mode = MODE.NORMAL

    def vol(self, _):
        logger.debug('VOL pressed')
        if self.button_mode == MODE.NORMAL:
            self.button_mode = MODE.VOLUME

        elif self.button_mode == MODE.VOLUME:
            logger.debug('Exiting VOLUME button mode, going back to NORMAL')
            self.button_mode = MODE.NORMAL

        elif self.button_mode == MODE.PLAYBACK:
            logger.debug('Getting next playback mode')
            self.model.next_playback_state()

    def run(self):
        logger.debug('Running player')

        logger.debug('Playing music started')

        first_song = self.model.get_first_song_path()
        logger.debug('Trying to play: {}'.format(first_song))
        self.play_song(first_song)
        while self.model.has_songs_in_playlist:
            self.process.wait()
            self.change_song(direction=DIR.FORWARD)

        logger.debug('Running player-- complete')
