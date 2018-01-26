#!/bin/python

import logging
import random
from collections import namedtuple
from itertools import cycle
from subprocess import call

from mpi3.model.db import Database
from constants import (
    DIRECTION as DIR
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Song(object):
    def __init__(self, song_id):
        self.id = song_id
        self.title = None
        self.path = None

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.path


class PlaybackStates(object):
    def __init__(self):
        _state_list = ['NORMAL', 'SHUFFLE', 'LOOP', 'REPEAT']
        _states = namedtuple('PLAYBACK_STATES', _state_list)
        self.mapping = {'NORMAL': ' ',
                        'SHUFFLE': 'X',
                        'LOOP': 'O',
                        'REPEAT': 'o'}

        self.iterator = cycle(_states(*_state_list))
        self.state = self.iterator.next()

    def next(self):
        self.state = self.iterator.next()
        return self.state

    def __str__(self):
        return self.mapping[self.state]

    def __repr__(self):
        return self.state

    def __eq__(self, other):
        return self.state == other


class Volume(object):
    def __init__(self):
        logger.debug('Initializing volume object')
        self.val = 2
        self.set_volume(self.val)

    def __str__(self):
        if self.get == 100:
            return '99'
        else:
            return '{:02.0f}'.format(self.get)

    @property
    def increase(self):
        if self.val < 20:
            self.val += 1
        self.set_volume(self.val)
        return self.get

    @property
    def decrease(self):
        if self.val > 1:
            self.val -= 1
        self.set_volume(self.val)
        return self.get

    @property
    def get(self):
        return self.val * 5

    def set_volume(self, val):
        self.val = val
        call(['amixer', 'sset', 'Master', '{}%'.format(self.get)])


class SongList(object):
    def __init__(self, db, filters=None, page_size=1):
        self.db = db
        self.filters = filters or dict()
        self.list = self.db.get_list(self.filters)
        self._cnt = self.db.get_count()
        self.page_size = page_size
        self.song_counter = 0
        self.page = 0  # Only incremented or set when you get a page of that number

    def __len__(self):
        return self._cnt

    def get_first_id(self):
        return self.list[self.song_counter]

    def get_next_id(self, state):
        if state in ('NORMAL', 'LOOP'):
            # Go to the next song in the list
            self.song_counter += 1

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

        out_id = self.list[self.song_counter] if self.song_counter < len(self.list) else None
        return out_id

    def get_prev_id(self, state):
        if state == 'NORMAL':
            self.song_counter -= 1

        elif state == 'LOOP':
            self.song_counter -= 1
            self.song_counter %= len(self.list)

        elif state == 'REPEAT':
            pass

        elif state == 'SHUFFLE':
            # Random is random :)
            return self.get_next_id('SHUFFLE')

        out_id = self.list[self.song_counter] if self.song_counter >= 0 else None
        return out_id

    def add_filter(self, artist=None, album=None):
        if not artist and not album:
            logger.warn('Attempted to add an empty filter.  Ignoring')

        if artist:
            self.filters['artist'] = artist
        if album:
            self.filters['album'] = album

        logger.debug('Added filter, regenerating list')
        self.list = self.db.get_list(self.filters)

        logger.debug('List regenerated, resetting song_counter')
        self.song_counter = 0

    def remove_filter(self, key):
        try:
            v = self.filters.pop(key)
            logger.debug('Popped the following filter: {}'.format(v))
            logger.debug('Removed filter, regenerating playlist')
            self.list = self.db.get_list(self.filters)

            logger.debug('List regenerated, resetting song_counter')
            self.song_counter = 0

        except KeyError as e:
            logger.error('Tried to remove filter from empty filter list')
            raise e

    def get_paginated_names(self, page):
        self.page = page
        # There are probably off-by-one-errors here
        offset = len(self.list) // (self.page_size * page) if page > 0 else 0
        limit_clause = 'LIMIT {row_count} OFFSET {offset}'.format(row_count=self.page_size,
                                                                  offset=offset)
        return self.db.get_by_id(self.list, limit_clause=limit_clause, titles=True)


class Model(object):
    def __init__(self, config):
        self.db = Database(config['music'])
        self.volume = Volume()

        self.playback_state = PlaybackStates()

        # Initializing playlist with all songs-- should probably change
        self.playlist = self.db.get_list(filters=[])

        self.playlist = SongList(db=self.db)
        self.viewlist = SongList(db=self.db, page_size=config['page_size'])

    def transfer_viewlist_to_playlist(self):
        # This will be called when a song in a playlist
        # is selected-- the filters just need to be
        # transferred over and the position saved (so if you start a playlist halfway through,
        # it'll be fine)
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
            return self.db.get_by_id(song_ids, paths=True)

    def get_names(self, song_ids):
        if song_ids is not None:
            return self.db.get_by_id(song_ids, titles=True)

    def get_first_song_id(self):
        logger.debug('Getting the first song')
        first_id = self.playlist.get_first_id()
        logger.debug('First song id is: {}'.format(first_id))
        return first_id

    def get_next_song(self, direction):
        next_id = None
        if direction == DIR.FORWARD:
            next_id = self.playlist.get_next_id(state=self.playback_state)
        elif direction == DIR.BACKWARD:
            next_id = self.playlist.get_prev_id(state=self.playback_state)

        return next_id
        # next_song = self.get_path(next_id)
        # if next_song:
        # return next_song[0]
