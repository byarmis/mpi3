#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import logging
import string
import os
import re

from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3

from mpi3 import xor
from mpi3.model.SQL import (
    CREATE_LIBRARY,
    INSERT_SONGS,
    GET_PLAYLIST,
    GET_BY_ID,
    GET_COUNT
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class NoSong(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class OpenConnection(object):
    def __init__(self, db_file):
        self.db_file = os.path.expanduser(db_file)
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()


class BatchAdder(object):
    def __init__(self, config):
        logger.info('Initializing BatchAdder')
        # _buffer is a list of tuples
        self._buffer = []
        self.buffer_size = config['buffer_load_size']
        self.db_file = config['library']

        self.stop_chars = {c: None for c in string.punctuation + string.digits}

        self.bad_tracks = {int(i) for i in config['bad_tracks']}

        if self.buffer_size > 500:
            logger.warning('A buffer load size of {} was selected, '
                           'but the max is 500'.format(self.buffer_size))
            self.buffer_size = 500

    def add(self, item):
        tags = self._extract_tags(item)

        self._buffer.append(tags)

        if len(self._buffer) >= self.buffer_size:
            self._add_buffer()

    def _extract_tags(self, f):
        logger.debug('Extracting tags for {}'.format(f))
        audio = MP3(f, ID3=EasyID3)

        title = audio.get('title')
        album = audio.get('album')
        artist = audio.get('artist')
        track_tuple = audio.get('tracknumber')

        if title:
            title = title[0].strip()
            sortable_title = title.lower().translate(self.stop_chars)
            if not sortable_title:
                # We removed too much!  Put it back?
                sortable_title = title
        else:
            title = None
            sortable_title = None

        album = album[0].strip() if album else None
        artist = artist[0].strip() if artist else None

        if track_tuple:
            track_split = track_tuple[0].split('/')
            track_number = int(track_split[0])
            total_tracks = int(track_split[1]) if len(track_split) > 1 else None
        else:
            track_number, total_tracks = None, None

        if track_number is None or track_number in self.bad_tracks:
            # If it starts with ##-, set ## to track number
            m = re.match(r'\A(\d*)\W', os.path.basename(f))
            if m:
                logger.info('Overwriting the current track number '
                            '({}) with an auto-extracted one ({})'.format(track_number,
                                                                          int(m.group(1))))
                track_number = int(m.group(1))

        t = (f, int(audio.info.length),
             title, sortable_title, album, artist, track_number, total_tracks)

        return t

    def _add_buffer(self):
        logger.debug('Adding batch of songs ({})'.format(len(self._buffer)))
        with OpenConnection(self.db_file) as db:
            db.executemany(INSERT_SONGS, self._buffer)

        self._buffer = []
        logger.debug('\t... complete')


class Database(object):
    def __init__(self, config):
        logger.info('Initializing Database')
        self.dirs = config['directory']
        self.db_file = os.path.expanduser(config['library'])
        self.adder = BatchAdder(config)
        self.count = None

        self.create_db()
        self.scan_libraries()
        self.get_count()

    def create_db(self):
        if os.path.isfile(self.db_file):
            logger.info('Library file ({}) exists and will be removed'.format(self.db_file))
            os.remove(self.db_file)
        else:
            logger.info('Library file ({}) does not exist and will be created'.format(self.db_file))

        with OpenConnection(self.db_file) as db:
            db.execute(CREATE_LIBRARY)

    def scan_libraries(self):
        logger.info('Scanning following directory(s):{}'.format('\n\t'.join(self.dirs)))

        for loc_raw in self.dirs:
            loc = os.path.expanduser(loc_raw)
            logger.debug('Scanning {raw}, expanded to {expanded}'.format(raw=loc_raw, expanded=loc))

            for (dirpath, _, filename) in os.walk(loc):
                if filename:
                    for f in filename:
                        if os.path.splitext(f)[1].lower() != '.mp3':
                            logger.debug('Found non-mp3 file: {}'.format(f))
                            continue

                        self.adder.add(os.path.join(dirpath, f))

    def get_count(self, filters=None):
        # If we haven't already gotten the count, get it
        # Otherwise, we can just return what we already have
        if self.count is None:
            with OpenConnection(self.db_file) as db:
                filter_statement = self._get_filters(filters)
                c = db.execute(GET_COUNT.format(filter_statement=filter_statement)).fetchall()[0][0]
            self.count = int(c)
        return self.count

    def get_list(self, filters=None, limit=None, offset=None):
        if filters and 'album' in filters:
            logger.debug('Songs should be sorted by track number')

            # TODO: Multi-disk albums?
            order_by = 'track_number ASC'
        else:
            logger.debug('Songs should be sorted alphabetically')
            order_by = 'sortable_title ASC'

        filter_statement = self._get_filters(filters)

        limit_clause = '' if limit is None else 'LIMIT %s' % limit
        offset_clause = '' if offset is None else 'OFFSET %s' % offset

        with OpenConnection(self.db_file) as db:
            q = GET_PLAYLIST.format(filter_statement=filter_statement,
                                    order_by=order_by,
                                    limit_clause=limit_clause,
                                    offset_clause=offset_clause)
            logger.info('Querying the DB with the following query:')
            logger.info(q)
            p = db.execute(q).fetchall()
            p = [i[0] for i in p]

        logger.debug('Retrieved following playlist: {}'.format(p))
        return p

    def get_by_id(self, ids, limit_clause='', paths=False, titles=False):
        assert paths | xor | titles, 'Paths xor titles have to be passed'
        get_type = None

        if paths is not None:
            logger.debug('Getting paths by ID')
            get_type = 'filepath'
        elif titles is not None:
            logger.debug('Getting titles by ID')
            get_type = 'title'

        res = None
        with OpenConnection(self.db_file) as db:
            try:
                res = db.execute(GET_BY_ID.format(get_type=get_type,
                                                  limit_clause=limit_clause), (ids,)).fetchall()[0]
                # Should return ((3, 'path'), (4,'path')...)
                # or ((3, 'name'), (4, 'name')...)
            except IndexError:
                raise NoSong('No songs found for {} = [{}]'.format(get_type, ','.join(ids)))

        if len(res) == 2:
            id_to_str = {res[0]: res[1]}
        else:
            id_to_str = dict(res)
        logger.debug('Dictionary acquired: {}'.format(id_to_str))

        try:
            return [id_to_str[i] for i in ids]
        except TypeError:
            return [id_to_str[ids]]

    @staticmethod
    def _get_filters(filters):
        if filters:
            filter_list = ['{} = {}'.format(k, v) for k, v in filters.items()]
            filter_statement = 'WHERE {}'.format('\nAND '.join(filter_list))
        else:
            filter_statement = ''
        return filter_statement
