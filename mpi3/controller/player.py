#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import subprocess
from threading import Event
from datetime import datetime as dt

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
        self.can_refresh = True

        initialize.setup_buttons(self.config,
                                 up=self.up,
                                 down=self.down,
                                 select=self.sel,
                                 play=self.play,
                                 volume=self.vol)

        self.initialize_mpg123()
        logger.debug('Player initialization complete')

        # First render-- complete rerender
        self.render(partial=False)
        self.last_refresh = dt.now()

    def initialize_mpg123(self):
        logger.debug('Initializing mpg123 process...')
        self.process = subprocess.Popen(['mpg123', '--remote'],
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE)
        # q = Queue()
# t = Thread(target=enqueue_output, args=(p.stdout, q))
# t.daemon = True  # thread dies with the program
# t.start()
#
# ... do other things here
#
# read line without blocking
# try:
#     line = q.get_nowait()  # or q.get(timeout=.1)
# except Empty:
#     print('no output yet')
#
# else:  # got line
#     pass
    # ... do something with line
    #     logger.debug('\t...complete')

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

    def play_song(self, song_path: str):
        # Plays song by ID
        if self.is_playing:
            logger.debug('Stopping current song')
            self.stop()

        logger.debug(song_path)
        logger.debug('Playing {}'.format(song_path))
        self.process.stdin.write('LOAD {}\n'.format(song_path).encode('utf-8'))
        self.is_playing = True

    def stop(self):
        self.process.stdin.write(b'STOP\n')
        self.is_playing = False
        logger.debug('Song stopped')

    def up(self, _):
        if self.button_mode == MODE.NORMAL:
            logger.debug('Moving up')
            redraw = self.model.menu.cursor_up()
            logger.debug('and rerendering {}'.format('partially' if redraw else 'totally'))
            self.render(partial=redraw)

        elif self.button_mode == MODE.VOLUME:
            vol = self.model.volume.increase
            logger.debug('Volume increased to {}'.format(vol))
            self.render(partial=True)

        elif self.button_mode == MODE.PLAYBACK:
            logger.info('Playing next song')
            self.change_song(direction=DIR.FORWARD)

    def down(self, _):
        if self.button_mode == MODE.NORMAL:
            logger.debug('Moving down')
            redraw = self.model.menu.cursor_down()
            self.render(partial=redraw)

        elif self.button_mode == MODE.VOLUME:
            logger.debug('Decreasing volume')
            vol = self.model.volume.decrease
            logger.debug('Volume decreased to {}'.format(vol))
            self.render(partial=True)

        elif self.button_mode == MODE.PLAYBACK:
            logger.info('Playing previous song')
            self.change_song(direction=DIR.BACKWARD)

    def sel(self, _):
        logger.debug('SELECT')

        if self.button_mode == MODE.NORMAL:
            logger.debug('clicking')
            self.can_refresh = False
            redraw = self.model.menu.on_click()
            self.can_refresh = True
            logger.debug('clicked')
            self.render(partial=redraw)
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
            self.process.stdin.write(b'PAUSE\n')
            logger.debug('Song paused')

        # Have to rerender to update the volume and playback mode info
        # Never do a full redraw when just changing one of those two
        self.render(partial=False)

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
        # Never do a full redraw when just changing one of those two
        self.render(partial=False)

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

        self.render(partial=False)

    def render(self, partial):
        self.view.render(title=self.model.title,
                         items=self.model.menu.items,
                         cursor_val=self.model.cursor_val,
                         partial=partial)

    def run(self):
        logger.debug('Running player')

        while True:
            # logger.debug('reading stdin')
            # for line in self.process.stdout:

            # logger.debug(self.process.stdout.communicate())
            # if sys.stdout.readline() == '@P 0\n':
            #     logger.debug('alsdjfalskdjfaslkdjfasldfkjjko')
            # logger.debug('read stdin')

            if self.can_refresh and \
                    (dt.now() - self.last_refresh).total_seconds() >= self.config['heartbeat_refresh']:
                logger.debug('Heartbeat rerender')
                self.render(partial=True)
                self.last_refresh = dt.now()


# import sys
# from subprocess import PIPE, Popen
# from threading import Thread
#
# from queue import Queue, Empty


# def enqueue_output(out, queue):
#     for line in iter(out.readline, b''):
#         queue.put(line)
#     out.close()
#
#
# p = Popen(['myprogram.exe'], stdout=PIPE, bufsize=1)

