#!/bin/python

import logging
import random
from itertools import cycle
from subprocess import call

from mpi3.model.db import Database

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

NORMAL = 'NORMAL'
SHUFFLE = 'SHUFFLE'
LOOP = 'LOOP'
REPEAT = 'REPEAT'
PLAYBACK_STATES = cycle((NORMAL, SHUFFLE, LOOP, REPEAT))


class Volume(object):
    def __init__(self):
        logger.debug('Initializing volume object')
        self.val = 2
        self.set_volume(self.val)

    @property
    def increase(self):
        if self.val < 19:
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
        self.filters = filters if filters is not None else []
        self.list = self.db.get_list(self.filters)
        self.page_size = page_size
        self.song_counter = 0

    def __len__(self):
        return len(self.list)

    def get_first_id(self):
        return self.list[self.song_counter]

    def get_next_id(self, state):
        if state in (NORMAL, LOOP):
            # Go to the next song in the list
            self.song_counter += 1

        if state == LOOP:
            # Wrap around
            self.song_counter %= len(self.list)

        elif state == REPEAT:
            # Play the same song over and over
            pass

        elif state == SHUFFLE:
            # Get a random new song ID that isn't the current one
            old = self.song_counter
            new = random.randint(0, len(self.list) - 1)
            while len(self.list) > 1 and old != new:
                # Make sure that we're getting a new song
                # ID if there is a new one to get
                # Worst case O(inf), average case O(1)
                new = random.randint(0, len(self.list) - 1)
            self.song_counter = new

        return self.list[self.song_counter]

    def get_prev_id(self, state):
        if state == NORMAL and self.song_counter > 0:
            self.song_counter -= 1

        elif state == LOOP:
            self.song_counter -= 1
            self.song_counter %= len(self.list)

        elif state == REPEAT:
            pass

        elif state == SHUFFLE:
            # Random is random :)
            return self.get_next_id(SHUFFLE)

        return self.list[self.song_counter]

    def get_paths(self):
        return self.db.get_by_id(self.list, limit_clause='', paths=True)

    def get_names(self):
        return self.db.get_by_id(self.list, limit_clause='', titles=True)

     def add_filter(self, artist=None, album=None):
        if not artist and not album:
            logger.warn('Attempted to add an empty filter.  Ignoring')

        if artist:
            self.filters.append('artist = {}'.format(artist))
        if album:
            self.filters.append('album = {}'.format(album))

        logger.debug('Added filter, regenerating list')
        self.list = self.library.get_playlist(self.filters)

        self.song_counter = 0

    def remove_filter(self):
        if self.filters:
            p = self.filters.pop()
            logger.debug('Popped the following filter: {}'.format(p))
            logger.debug('Removed filter, regenerating playlist')
            self.list = self.library.get_playlist(self.filters)
            self.song_counter = 0

        else:
            logger.error('Tried to remove filter from empty filter list')

    def get_paginated_names(self, page):
        # There are probably off-by-one-errors here
        offset = len(self.list) // (self.page_size * page) if page > 0 else 0
        limit_clause = 'LIMIT {row_count} OFFSET {offset}'.format(row_count=self.page_size,
                                                                  offset=offset)
        return self.db.get_by_id(self.list, limit_clause=limit_clause, titles=True)


class Library(object):
    def __init__(self, music_config):
        logger.debug('Initializing the library')
        self.music_config = music_config
        self.db = Database(self.music_config)

    def get_playlist(self, filters):
        return self.db.get_list(filters)

    def get_path_by_id(self, song_id):
        raise NotImplementedError


class Model(object):
    def __init__(self, config):
        self.library = Library(config['music'])
        self.volume = Volume()

        self.playback_state = PLAYBACK_STATES.next()

        # Initializing playlist with all songs-- should probably change
        self.playlist = self.library.get_playlist(filters=[])

        self.playlist = SongList(db=self.library.db)
        self.viewlist = SongList(db=self.library.db, page_size=config['page_size'])

    def transfer_viewlist_to_playlist(self):
        # This will be called when a song in a playlist
        # is selected-- the filters just need to be
        # transferred over and the position saved (so if you start a playlist halfway through,
        # it'll be fine)
        self.playlist.filters = list(self.viewlist.filters)
        self.playlist.song_counter = self.viewlist.song_counter

    @property
    def has_songs_in_playlist(self):
        return self.playlist.song_counter < len(self.playlist)

    def next_playback_state(self):
        logger.debug('Playback state was: {}...'.format(self.playback_state))
        self.playback_state = PLAYBACK_STATES.next()
        logger.debug('... and is now {}'.format(self.playback_state))


