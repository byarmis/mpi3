#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import subprocess
from threading import Event

from mpi3 import initialize
from mpi3.model.model import Model
from mpi3.view.view import View
from mpi3.model.constants import (
    DIRECTION as DIR,
    BUTTON_MODE as MODE,
)

logger = logging.getLogger(__name__)


# FIXME: What happens when we reach the end of a song and it just stops?

class Player(object):
    def __init__(self, args):
        self.config = initialize.get_config(args.config_file)
        self.model = Model(config=self.config, play_song=self.play_song)
        self.view = View(config=self.config)

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
        logger.debug('Player initialization complete')

        # First render-- complete rerender
        self.view.render(title='TITLE', items=['first', 'second', 'third'], cursor_val=self.model.cursor_val,
                         partial=False)

    def initialize_mpg123(self):
        logger.debug('Initializing mpg123 process...')
        self.process = subprocess.Popen(['mpg123', '--remote'],
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE)
        logger.debug('\t...complete')

    def change_song(self, direction):
        if self.process.poll():
            logger.debug('Player is not running.  Starting...')
            self.initialize_mpg123()

        logger.debug('Getting next song')

        # PEP-572 would be helpful here, I think?
        next_song = self.model.get_next_song(direction)

        if next_song:
            logger.debug("Next song's id is: {}".format(next_song))
            logger.debug('Playing next song')
            self.play_song(next_song)
            logger.debug('Playing next song started')

        else:
            logger.debug("There isn't a next song to play.  Stopping")
            self.stop()

    def play_song(self, song_id):
        # Plays song by ID
        song_path = self.model.get_path(song_id)[0]
        if self.is_playing:
            logger.debug('Stopping current song')
            self.stop()

        logger.debug('Playing {}'.format(song_path))
        self.process.stdin.write('LOAD {}\n'.format(song_path))
        self.is_playing = True

    def stop(self):
        self.process.stdin.write('STOP\n')
        self.is_playing = False
        logger.debug('Song stopped')

    def up(self, _):
        if self.button_mode == MODE.NORMAL:
            logger.debug('Moving up')
            redraw = self.model.menu.cursor_up()
            self.view.render(page=self.model.page,
                             cursor_val=self.model.cursor_val,
                             title=self.model.title,
                             partial=redraw)

        elif self.button_mode == MODE.VOLUME:
            vol = self.model.volume.increase
            logger.debug('Volume increased to {}'.format(vol))

        elif self.button_mode == MODE.PLAYBACK:
            logger.info('Playing next song')
            self.change_song(direction=DIR.FORWARD)

    def down(self, _):
        if self.button_mode == MODE.NORMAL:
            logger.debug('Moving down')
            redraw = self.model.menu.cursor_down()
            self.view.render(page=self.model.page,
                             cursor_val=self.model.cursor_val,
                             title=self.model.title,
                             partial=redraw)

        elif self.button_mode == MODE.VOLUME:
            logger.debug('Decreasing volume')
            vol = self.model.volume.decrease
            logger.debug('Volume decreased to {}'.format(vol))

        elif self.button_mode == MODE.PLAYBACK:
            logger.info('Playing previous song')
            self.change_song(direction=DIR.BACKWARD)

    def sel(self, _):
        logger.debug('SELECT')

        if self.button_mode == MODE.NORMAL:
            raise NotImplementedError("Clicking on things isn't working yet.  Shut up")
            self.model.selected.on_click()
            self.view.render(page=self.model.page,
                             cursor_val=self.model.cursor_val,
                             title=self.model.title,
                             partial=redraw)
            return

        elif self.button_mode == MODE.VOLUME:
            # MUTE
            vol = self.model.volume.mute
            if vol:
                logger.debug('Volume unmuted and changed to {}'.format(vol))
            else:
                logger.debug('Volume muted')

        elif self.button_mode == MODE.PLAYBACK:
            # Pause
            self.is_playing = False
            self.process.stdin.write('PAUSE\n')
            logger.debug('Song paused')

        # Have to rerender to update the volume and playback mode info
        self.view.render(page=self.model.page,
                         cursor_val=self.model.cursor_val,
                         title=self.model.title,
                         partial=False)  # Never do a full redraw when just changing one of those two

    def play(self, _):
        logger.debug('PLAY')

        if self.button_mode == MODE.NORMAL:
            logger.debug('Changing button mode to PLAYBACK')
            self.button_mode = MODE.PLAYBACK

        elif self.button_mode == MODE.VOLUME:
            logger.debug('Getting next playback mode')
            self.model.next_playback_state()
            # Setting the button mode back to normal
            self.button_mode = MODE.NORMAL

        elif self.button_mode == MODE.PLAYBACK:
            logger.debug('Exiting PLAYBACK button mode, going back to NORMAL')
            self.button_mode = MODE.NORMAL

        # Have to rerender to update the volume and playback mode info
        self.view.render(page=self.model.page,
                         cursor_val=self.model.cursor_val,
                         title=self.model.title,
                         partial=False)  # Never do a full redraw when just changing one of those two

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
            # Setting the button mode back to normal
            self.button_mode = MODE.NORMAL

        # Have to rerender to update the volume and playback mode info
        self.view.render(page=self.model.page,
                         cursor_val=self.model.cursor_val,
                         title=self.model.title,
                         partial=False)  # Never do a full redraw when just changing one of those two

    def run(self):
        logger.debug('Running player')

        while True:
            Event().wait(1)
        #
        # # START Testing
        # logger.debug('Playing music started')
        #
        # first_song = self.model.get_first_song_id()
        # logger.debug('Trying to play: {}'.format(first_song))
        # self.play_song(first_song)
        # while self.model.has_songs_in_playlist:
        #     self.process.wait()
        #     self.change_song(direction=DIR.FORWARD)
        #
        # # END Testing

        logger.debug('Running player-- complete')
