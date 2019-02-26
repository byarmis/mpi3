#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import subprocess
from datetime import datetime as dt
from queue import Queue, Empty
from threading import Thread

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


class NonBlockingStreamReader:
    def __init__(self, stream):
        """
        stream: the stream to read from.
                Usually a process' stdout or stderr.
                
        from http://eyalarubas.com/python-subproc-nonblock.html
        """

        self._s = stream
        self._q = Queue()

        def _populate_queue(stream_provider, queue):
            """
            Collect lines from 'stream_provider' and put them in 'queue'.
            """

            while True:
                line = stream_provider.readline()
                assert line, 'Unexpected end of stream'
                queue.put(line)

        self._t = Thread(target=_populate_queue,
                         args=(self._s, self._q))
        self._t.daemon = True
        self._t.start()  # start collecting lines from the stream

    def readline(self, timeout: float = None):
        try:
            return self._q.get(block=timeout is not None,
                               timeout=timeout).strip()
        except Empty:
            return None


class MusicPlayer:
    def __init__(self) -> None:
        self.process = subprocess.Popen(['mpg123', '--remote'],
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        bufsize=1)
        self._write('SILENCE')

        self.stream_reader = NonBlockingStreamReader(self.process.stdout)

        self.last_state = None
        self.last_poll = None

    def _write(self, msg: str) -> None:
        self.process.stdin.write(str.encode(msg + '\n'))
        self.process.stdin.flush()

    def poll(self) -> None:
        self.last_poll = dt.now()
        self.last_state = self.stream_reader.readline() or self.last_state

    def play(self, song_path: str) -> None:
        if self.process.poll():
            logger.warning('Reinitializing MusicPlayer')
            self.__init__()

        # Plays song by ID
        if self.state == PLAYBACK_STATES.PLAY:
            logger.debug('Stopping current song')
            self.stop()

        logger.debug('Playing {}'.format(song_path))

        self._write('LOAD {}'.format(song_path))

    def stop(self) -> None:
        self._write('STOP')
        logger.debug('Song stopped')

    def pause(self) -> None:
        self._write('PAUSE')
        logger.debug('Song paused')

    @property
    def is_paused(self) -> bool:
        return mpg_123_STATES.get(self.state) == PLAYBACK_STATES.PAUSE

    @property
    def is_playing(self) -> bool:
        return mpg_123_STATES.get(self.state) == PLAYBACK_STATES.PLAY

    @property
    def state(self) -> mpg_123_STATES:
        if self.state is None:
            self.poll()

        if (dt.now() - self.last_poll).total_seconds() > 1:
            self.poll()
        return mpg_123_STATES.get(self.last_state)


class MPi3Player(object):
    def __init__(self, args):
        self.player = MusicPlayer()
        self.config = initialize.get_config(args.config_file)
        self.model = Model(config=self.config, play_song=self.player.play)
        self.view = View(config=self.config)

        self.button_mode = MODE.NORMAL
        self.can_refresh = True

        initialize.setup_buttons(self.config,
                                 up=self.up,
                                 down=self.down,
                                 select=self.sel,
                                 play=self.play,
                                 volume=self.vol)

        logger.debug('Player initialization complete')

        # First render-- complete rerender
        self.render(partial=False)
        self.last_refresh = dt.now()

    def change_song(self, direction):
        logger.debug('Getting next song')

        # PEP-572 would be helpful here, I think? I am the walrus coo coo ca choo
        next_song = self.model.get_next_song(direction)

        if next_song is not None:
            self.player.play(next_song.song_path)

        else:
            logger.debug("There isn't a next song to play.  Stopping")
            self.player.stop()

    def up(self, _):
        if self.button_mode == MODE.NORMAL:
            logger.debug('Moving up')
            redraw = self.model.menu.cursor_up()
            logger.debug('and re-rendering {}'.format('partially' if redraw else 'totally'))
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
            self.model.volume.mute()

        elif self.button_mode == MODE.PLAYBACK:
            # Pause
            self.player.pause()

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

            music_state = self.player.state
            if music_state == PLAYBACK_STATES.DONE:
                self.change_song(direction=DIR.FORWARD)

            if self.can_refresh and \
                    (dt.now() - self.last_refresh).total_seconds() >= self.config['heartbeat_refresh']:
                logger.debug('Heartbeat re-render')
                self.render(partial=True)
                self.last_refresh = dt.now()
