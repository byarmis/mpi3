#!/bin/python

import logging
from itertools import cycle
from subprocess import call
from mpi3.model.db import Database, OpenConnection

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

GET_PLAYLIST = '''
SELECT id 
FROM library {filter_statement} 
ORDER BY {order_by}
;'''

GET_PATH_BY_ID = '''
SELECT filepath
FROM library
WHERE id = ?
;'''

PLAYBACK_STATES = cycle(('NORMAL', 'SHUFFLE', 'LOOP', 'REPEAT'))


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


class Library(object):
    def __init__(self, music_config):
        logger.debug('Initializing the library')
        self.music_config = music_config
        self.db = Database(self.music_config)

    def get_playlist(self, filters):
        filter_statement = 'WHERE {}'.format('AND '.join(filters)) if filters else ''
        if filters and any('album' in f for f in filters):
            logger.debug('Songs should be sorted by track number')

            # TODO: Multi-disk albums?
            order_by = 'track_number ASC'
        else:
            logger.debug('Songs should be sorted alphabetically')
            order_by = 'sortable_title ASC'

        with OpenConnection(self.music_config['library']) as db:
            p = db.execute(GET_PLAYLIST.format(filter_statement=filter_statement,
                                               order_by=order_by)).fetchall()
            p = [i[0] for i in p]

        logger.debug('Retrieved following playlist: {}'.format(p))
        return p

    def get_path_by_id(self, song_id):
        with OpenConnection(self.music_config['library']) as db:
            logger.debug('Getting path for song id: {}'.format(song_id))
            path = db.execute(GET_PATH_BY_ID, (song_id,)).fetchall()[0][0]
        logger.debug('Path acquired: {}'.format(path))
        return path


class Model(object):
    def __init__(self, config):
        self.library = Library(config['music'])
        self.volume = Volume()

        self.song_counter = 0
        self.filters = []

        self.playback_state = PLAYBACK_STATES.next()

        # Initializing playlist with all songs-- should probably change
        self.playlist = self.library.get_playlist(self.filters)

    @property
    def has_songs_in_playlist(self):
        return self.song_counter < len(self.playlist)

    def next_playback_state(self):
        logger.debug('Playback state was: {}...'.format(self.playback_state))
        self.playback_state = PLAYBACK_STATES.next()
        logger.debug('... and is now {}'.format(self.playback_state))

    def get_first(self):
        if self.playlist:
            return self.library.get_path_by_id(self.playlist[0])

        else:
            logger.warn('Cannot get first song-- empty playlist')

    def get_next(self):
        self.song_counter += 1

        if self.playback_state == 'LOOP':
            if self.song_counter == len(self.playlist):
                self.song_counter = 0
        elif self.playback_state == 'REPEAT':
            self.song_counter -= 1

        elif self.playback_state in ('NORMAL', 'SHUFFLE'):
            if self.song_counter == len(self.playlist):
                return None

        next_id = self.playlist[self.song_counter]
        return self.library.get_path_by_id(next_id)

    def get_prev(self):
        self.song_counter -= 1
        if self.song_counter < 0:
            self.song_counter = len(self.playlist) - 1

        prev_id = self.playlist[self.song_counter]
        return self.library.get_path_by_id(prev_id)

    def add_filter(self, artist=None, album=None):
        if not artist and not album:
            logger.warn('Attempted to add an empty filter.  Ignoring')

        if artist:
            self.filters.append('artist = {}'.format(artist))
        if album:
            self.filters.append('album = {}'.format(album))

        logger.debug('Added filter, regenerating playlist')
        self.playlist = self.library.get_playlist(self.filters)

        self.song_counter = 0

    def remove_filter(self):
        if self.filters:
            p = self.filters.pop()
            logger.debug('Popped the following filter: {}'.format(p))
            logger.debug('Removed filter, regenerating playlist')
            self.playlist = self.library.get_playlist(self.filters)
            self.song_counter = 0

        else:
            logger.error('Tried to remove filter from empty filter list')
