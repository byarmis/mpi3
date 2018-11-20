#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import random
from collections import namedtuple
from itertools import cycle
from subprocess import call

from mpi3.model.db import Database
from mpi3.model.navigation import Menu, Title
from mpi3.model.constants import (
    DIRECTION as DIR
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

DATABASE = None


class Song(object):
    def __init__(self, song_id):
        global DATABASE
        self.id = song_id
        self.title = DATABASE.get_by_id(song_id, titles=True)
        self.path = DATABASE.get_by_id(song_id, paths=True)

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.path


class PlaybackStates(object):
    def __init__(self):
        _state_list = ['NORMAL', 'SHUFFLE', 'LOOP', 'REPEAT']
        _states = namedtuple('PLAYBACK_STATES', _state_list)
        self._mapping = {'NORMAL': ' ',
                         'SHUFFLE': 'X',
                         'LOOP': 'O',
                         'REPEAT': 'o'}

        self._iterator = cycle(_states(*_state_list))
        self.state = self.next()

    def next(self):
        self.state = next(self._iterator)
        return self.state

    def __str__(self):
        return self._mapping[self.state]

    def __repr__(self):
        return self.state

    # def __eq__(self, other):
    #     return self.state == other.state


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

        try:
            self.current_volume = desired_default

        except IndexError:
            # Get the difference between the desired and actual possible
            diff = [desired_default - i for i in self._array]

            for loc, val in enumerate(diff[::-1]):
                # Find the value that's closest to the desired
                # Go highest to lowest, find the first one that's less than desired
                if val > 0:
                    self.current_volume = self._array[loc]
                    break
            else:
                # Can't find anything close. Set the first non-mute
                logger.warn('Cannot find any volumes less than the desired default.  ' \
                            'Setting it to zero')
                self.current_volume = 0

        self._set_volume()
        self._old_volume = None

    def __str__(self):
        if self.current_volume == 100:
            return '/\\'  # Max
        elif self.current_volume == 0:
            return '\/'  # Min
        else:
            return '{:02.0f}'.format(self.current_volume)

    def _change_val(self, amt):
        assert amt == 1 or amt == -1, \
            'Unknown volume change amount: {}'.format(amt)
        v = self.current_volume
        if amt < 0 and v == 0:
            logger.info('Cannot go lower than 0')
        elif amt > 0 and v == 100:
            logger.info('Cannot go higher than 100')
        else:
            a = self._array
            self.current_volume = a[a.index(v) + amt]
            self._set_volume()

    def _set_volume(self):
        call(['amixer', 'sset', 'Master', '{}%'.format(self.current_volume)])

    @property
    def increase(self):
        return self._change_val(1)

    @property
    def decrease(self):
        # TODO: Mute vs 0%?  How's the noise?
        return self._change_val(-1)

    @property
    def mute(self):
        if self.current_volume > 0:
            # Mute

            # Save the current volume
            self._old_volume = self.current_volume
            # Set the new value
            self.current_volume = 0

        elif self._old_volume is not None:
            # Unmute
            self.current_volume = self._old_volume
            # Null it out?
            self._old_volume = None

        else:
            # lol idk?
            logger.warn('Not sure to mute or unmute\n\tcurrent volume: {}\n\told volume: {}'.format(
                self.current_volume,
                self._old_volume
            ))

        self._set_volume()
        return self.current_volume


class SongList(object):
    def __init__(self, db, filters=None, page_size=1):
        self.db = db
        self.filters = filters or dict()
        self.list = self.db.get_list(self.filters)
        self._cnt = self.db.get_count()
        self.page_size = page_size
        self.song_counter = 0
        self.page = 0

    def __len__(self):
        return self._cnt

    @property
    def get_id(self):
        if 0 <= self.song_counter < self._cnt:
            return self.list[self.song_counter]

        else:
            return None

    def get_next_id(self, state):
        if state in ('NORMAL', 'LOOP'):
            # Go to the next song in the list
            if self.song_counter < self._cnt:
                self.song_counter += 1
            else:
                return None

        if state == 'LOOP':
            # Wrap around
            self.song_counter %= len(self.list)

        elif state == 'REPEAT':
            # Play the same song over and over
            pass

        elif state == 'SHUFFLE':
            # Get a random new song ID that isn't the current one
            old = self.song_counter
            new = random.randint(0, len(self.list) - 1)
            while len(self.list) > 1 and old != new:
                # Make sure that we're getting a new song
                # ID if there is a new one to get
                # Worst case O(inf), expected case O(1)
                new = random.randint(0, len(self.list) - 1)
            self.song_counter = new

        out_id = self.list[self.song_counter]
        return out_id

    def get_prev_id(self, state):
        if state == 'NORMAL':
            if self.song_counter > 0:
                self.song_counter -= 1
            else:
                return None

        elif state == 'LOOP':
            self.song_counter -= 1
            if self.song_counter < 0:
                self.song_counter %= len(self.list)

        elif state == 'REPEAT':
            pass

        elif state == 'SHUFFLE':
            # Random is random :)
            return self.get_next_id('SHUFFLE')

        out_id = self.list[self.song_counter]
        return out_id

    # def add_filter(self, artist=None, album=None):
    #     if not artist and not album:
    #         logger.warn('Attempted to add an empty filter.  Ignoring')
    #
    #     if artist:
    #         self.filters['artist'] = artist
    #     if album:
    #         self.filters['album'] = album
    #
    #     logger.debug('Added filter, regenerating list')
    #     self.list = self.db.get_list(self.filters)
    #
    #     logger.debug('List regenerated, resetting song_counter')
    #     self.song_counter = 0
    #
    # def remove_filter(self, key):
    #     try:
    #         v = self.filters.pop(key)
    #         logger.debug('Popped the following filter: {}'.format(v))
    #         logger.debug('Removed filter, regenerating playlist')
    #         self.list = self.db.get_list(self.filters)
    #
    #         logger.debug('List regenerated, resetting song_counter')
    #         self.song_counter = 0
    #
    #     except KeyError as e:
    #         logger.error('Tried to remove filter from empty filter list')
    #         raise e
    #
    # def get_paginated_names(self, page):
    #     self.page = page
    #     # There are probably off-by-one-errors here
    #     offset = len(self.list) // (self.page_size * page) if page > 0 else 0
    #     limit_clause = 'LIMIT {row_count} OFFSET {offset}'.format(row_count=self.page_size,
    #                                                               offset=offset)
    #     return self.db.get_by_id(self.list, limit_clause=limit_clause, titles=True)


class Model(object):
    def __init__(self, config):
        global DATABASE
        DATABASE = Database(config['music'])
        self.volume = Volume(config['volume'])

        self.playback_state = PlaybackStates()

        self.playlist = None
        self.viewlist = None
        self.menu = Menu(config=config, db=DATABASE)
        self.title = Title(state=self.playback_state, vol=self.volume.current_volume)

    def transfer_viewlist_to_playlist(self):
        # This will be called when a song in a playlist
        # is selected-- the filters need to be
        # transferred over and the position saved (so if you start a playlist
        # halfway through, it'll be fine)
        self.playlist.filters = {k: v for k, v in self.viewlist.filters.items()}
        self.playlist.song_counter = self.viewlist.song_counter

    @property
    def has_songs_in_playlist(self):
        return self.playlist.song_counter < len(self.playlist)

    def next_playback_state(self):
        logger.debug('Playback state was: {}...'.format(self.playback_state))
        self.playback_state = self.playback_state.next()
        logger.debug('... and is now {}'.format(self.playback_state))

    def get_path(self, song_ids):
        # Gets the path or paths for one or more songs
        if song_ids is not None:
            return DATABASE.get_by_id(song_ids, paths=True)

    def get_names(self, song_ids):
        if song_ids is not None:
            return DATABASE.get_by_id(song_ids, titles=True)

    def get_next_song(self, direction):
        next_id = None
        if direction == DIR.FORWARD:
            next_id = self.playlist.get_next_id(state=self.playback_state)
        elif direction == DIR.BACKWARD:
            next_id = self.playlist.get_prev_id(state=self.playback_state)

        return next_id

    @property
    def cursor_val(self):
        return self.menu._menu_stack.peek().cursor.value
