#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import random
from collections import namedtuple
from itertools import cycle
from subprocess import call

from mpi3.model.db import Database
from mpi3.model.navigation import Menu, Title
from mpi3.model.menu_items import SongButton
from mpi3.model.constants import (
    DIRECTION as DIR
)

logger = logging.getLogger(__name__)


class PlaybackStates(object):
    def __init__(self):
        _state_list = ['NORMAL', 'SHUFFLE', 'LOOP', 'REPEAT']
        _states = namedtuple('PLAYBACK_STATES', _state_list)
        self._mapping = {'NORMAL': ' ',
                         'SHUFFLE': 'X',
                         'LOOP': 'O',
                         'REPEAT': 'o'}

        self._iterator = cycle(_states(*_state_list))
        self.state = next(self._iterator)

    def next(self):
        self.state = next(self._iterator)

    def __str__(self):
        return self._mapping[self.state]

    def __repr__(self):
        return self.state


class Volume(object):
    #  0   2  4  6  8
    # {10} 20 30 40 50
    #  60  70 80 90 100

    def __init__(self, config):
        logger.debug('Initializing volume object')

        desired_default = config['default']
        low_vol_stepsize = config['stepsize_low']
        high_vol_stepsize = config['stepsize_high']
        low_vol_max = config['low_max']

        self._array = list(range(0, low_vol_max, low_vol_stepsize))
        self._array += list(range(low_vol_max, 100 + high_vol_stepsize, high_vol_stepsize))

        for loc, val in enumerate(self._array):
            if val == desired_default:
                self._current_vol_ptr = loc
                break

        else:
            # Get the difference between the desired and actual possible
            diff = [desired_default - i for i in self._array]

            for loc, val in enumerate(diff[::-1]):
                # Find the value that's closest to the desired
                # Go highest to lowest, find the first one that's less than desired
                if val > 0:
                    self._current_vol_ptr = len(diff) - loc
                    break
            else:
                # Can't find anything close. Set the first non-mute
                logger.warning('Cannot find any volumes less than the desired default.  '
                               'Setting it to as quiet as possible')
                self._current_vol_ptr = 1

        self._set_volume()
        self._old_vol_ptr = None

    @property
    def current_volume(self):
        return self._array[self._current_vol_ptr]

    def __str__(self):
        if self.current_volume == 100:
            return '/\\'  # Max
        elif self.current_volume == 0:
            return '\\/'  # Min
        else:
            return '{:02.0f}'.format(self.current_volume)

    def _change_val(self, amt):
        if not 0 <= self._current_vol_ptr + amt <= len(self._array):
            logger.debug('Cannot go out of bounds for volume change, not doing anything')
        else:
            self._current_vol_ptr += amt
            self._set_volume()

        return self.current_volume

    def _set_volume(self):
        call(['amixer', 'sset', 'PCM', '{}%'.format(self.current_volume)])

    @property
    def increase(self):
        return self._change_val(1)

    @property
    def decrease(self):
        # TODO: Mute vs 0%?  How's the noise?
        return self._change_val(-1)

    @property
    def mute(self):
        if self._current_vol_ptr > 0:
            # Mute

            # Save the current volume
            self._old_vol_ptr = self._current_vol_ptr
            # Set the new value
            self._current_vol_ptr = 0

        elif self._old_vol_ptr is not None:
            # Unmute
            self._current_vol_ptr = self._old_vol_ptr
            # and null it out?
            self._old_vol_ptr = None

        else:
            # lol idk?
            logger.warning('Not sure to mute or unmute\n\tcurrent volume: {}\n\told volume: {}'.format(
                    self._current_vol_ptr,
                    self._old_vol_ptr
            ))

        self._set_volume()
        return self.current_volume


class SongList(object):
    def __init__(self, db, play_song, page_size, filters=None):
        self.db = db
        self.filters = filters or dict()
        self._cnt = self.db.get_count()
        self.page_size = page_size
        self.play_song = play_song
        self.song_counter = 0
        self.page = 0

        self.id_list = []
        self.title_list = []
        self.path_list = []

        self.refresh_list()

    def __iter__(self):
        for song_id, title, path in zip(self.id_list, self.title_list, self.path_list):
            yield SongButton(song_id=song_id,
                             song_title=title,
                             song_path=path,
                             play_song=self.play_song)

    def __len__(self):
        return self._cnt

    def refresh_list(self):
        self.id_list = self.db.get_list(filters=self.filters,
                                        limit=self.page_size,
                                        offset=self.page * self.page_size)
        self.title_list = self.db.get_by_id(ids=self.id_list, titles=True)
        self.path_list = self.db.get_by_id(ids=self.id_list, paths=True)

    @property
    def selected_id(self):
        start = self.page * self.page_size
        end = self.page_size + (self.page * self.page_size)
        if not (start <= self.song_counter <= end):
            # Go to the next page and get it
            # Also should work for random song changes that might skip to a random page
            self.page = self.song_counter // self.page_size
            self.refresh_list()

        return self.id_list[self.song_counter - start]

    def get_next_id(self, state):
        if state in ('NORMAL', 'LOOP'):
            # Go to the next song in the list
            if self.song_counter < self._cnt:
                self.song_counter += 1
            else:
                return None

        if state == 'LOOP':
            # Wrap around
            self.song_counter %= self._cnt

        elif state == 'REPEAT':
            # Play the same song over and over
            pass

        elif state == 'SHUFFLE':
            # Get a random new song ID that isn't the current one
            old = self.song_counter

            # randint is inclusive, we want exclusive
            new = random.randint(0, self._cnt - 1)

            while len(self.id_list) > 1 and old != new:
                # Make sure that we're getting a new song
                # ID if there is a new one to get
                # Worst case O(inf), expected case O(1)
                new = random.randint(0, self._cnt - 1)
            self.song_counter = new

        return self.selected_id

    def get_prev_id(self, state):
        if state == 'NORMAL':
            if self.song_counter > 0:
                self.song_counter -= 1
            else:
                return None

        elif state == 'LOOP':
            self.song_counter -= 1
            if self.song_counter < 0:
                self.song_counter %= self._cnt

        elif state == 'REPEAT':
            return self.song_counter

        elif state == 'SHUFFLE':
            # Random is random :)
            return self.get_next_id('SHUFFLE')

        return self.selected_id


class Model(object):
    def __init__(self, config, play_song):
        self.database = Database(config['music'])
        self.volume = Volume(config['volume'])

        self.playback_state = PlaybackStates()

        self.playlist = SongList(db=self.database, page_size=config['computed']['page_size'], play_song=play_song)
        self.menu = Menu(config=config, db=self.database)
        self.title = Title(state=self.playback_state, vol=self.volume.current_volume)

    def transfer_viewlist_to_playlist(self):
        # This will be called when a song in a playlist is selected-- the filters need to be
        # transferred over and the position saved (so if you start a playlist halfway through, it'll be fine)
        self.playlist.filters = {k: v for k, v in self.menu.viewlist.filters.items()}
        self.playlist.song_counter = self.menu.viewlist.song_counter

    @property
    def has_songs_in_playlist(self):
        return self.playlist.song_counter < len(self.playlist)

    def next_playback_state(self):
        logger.debug('Playback state was: {}...'.format(self.playback_state))
        self.playback_state.next()
        logger.debug('... and is now {}'.format(self.playback_state))

    def get_path(self, song_ids):
        # Gets the path or paths for one or more songs
        if song_ids is not None:
            return self.database.get_by_id(song_ids, paths=True)

    def get_names(self, song_ids):
        if song_ids is not None:
            return self.database.get_by_id(song_ids, titles=True)

    def get_next_song(self, direction):
        next_id = None
        if direction == DIR.FORWARD:
            next_id = self.playlist.get_next_id(state=self.playback_state)
        elif direction == DIR.BACKWARD:
            next_id = self.playlist.get_prev_id(state=self.playback_state)

        return next_id

    @property
    def cursor_val(self):
        return self.menu._menu_stack.peek().cursor_val

    @property
    def page(self):
        return self.menu._menu_stack.peek()
