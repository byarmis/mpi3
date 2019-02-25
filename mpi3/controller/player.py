#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from subprocess import PIPE, Popen
from threading import Thread

from queue import Queue, Empty

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
    PLAYBACK_STATES,
    mpg_123_STATES,
)

logger = logging.getLogger(__name__)

from threading import Thread
from queue import Queue, Empty


class NonBlockingStreamReader:

    def __init__(self, stream):
        '''
        stream: the stream to read from.
                Usually a process' stdout or stderr.
        '''

        self._s = stream
        self._q = Queue()
        self.music_playback_state = None

        def _populateQueue(stream, queue):
            '''
            Collect lines from 'stream' and put them in 'quque'.
            '''

            while True:
                line = stream.readline()
                if line:
                    queue.put(line)
                else:
                    raise UnexpectedEndOfStream

        self._t = Thread(target=_populateQueue,
                         args=(self._s, self._q))
        self._t.daemon = True
        self._t.start()  # start collecting lines from the stream

    def readline(self, timeout=None):
        try:
            g = self._q.get(block=timeout is not None,
                            timeout=timeout).strip()
            try:
                return mpg_123_STATES[g]
            except KeyError:
                return None
        except Empty:
            return None


class UnexpectedEndOfStream(Exception):
    pass


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

        self.music_playback_state = None

    def initialize_mpg123(self):
        logger.debug('Initializing mpg123 process...')
        self.process = subprocess.Popen(['mpg123', '--remote'],
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        bufsize=1)
        self.process.stdin.write(b'SILENCE\n')
        self.process.stdin.flush()

        self.nbsr = NonBlockingStreamReader(self.process.stdout)

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
            self.play_song(next_song.song_path)
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
        self.process.stdin.flush()
        self.is_playing = True

    def stop(self):
        self.process.stdin.write(b'STOP\n')
        self.process.stdin.flush()
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
            self.process.stdin.flush()
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
        import time

        while True:
            time.sleep(0.1)

            music_state = self.nbsr.readline()
            if music_state == PLAYBACK_STATES.DONE:
                self.change_song(direction=DIR.FORWARD)

            if self.can_refresh and \
                    (dt.now() - self.last_refresh).total_seconds() >= self.config['heartbeat_refresh']:
                logger.debug('Heartbeat rerender')
                self.render(partial=True)
                self.last_refresh = dt.now()
