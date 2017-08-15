#!/bin/python

import sqlite3
import logging
import string
import os
import re

from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

CREATE_LIBRARY = '''
CREATE TABLE library (
      id             INTEGER PRIMARY KEY AUTOINCREMENT
    , filepath       TEXT UNIQUE NOT NULL
    , length         INTEGER
    , title          TEXT
    , sortable_title TEXT
    , album          TEXT
    , artist         TEXT
    , track_number   INTEGER
    , total_tracks   INTEGER
);
'''

INSERT_SONGS = '''
INSERT INTO library 
  (filepath, length, title, sortable_title, album, artist, track_number, total_tracks) 
VALUES (?,?,?,?,?,?,?,?);
'''


class OpenConnection(object):
    def __init__(self, db_file):
        self.db_file = db_file
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
        logger.info('Adding batch of songs ({})'.format(len(self._buffer)))
        with OpenConnection(self.db_file) as db:
            db.executemany(INSERT_SONGS, self._buffer)

        self._buffer = []


class Database(object):
    def __init__(self, config):
        logger.info('Initializing Database')
        self.dirs = config['directory']
        self.db_file = config['library']
        self.adder = BatchAdder(config)

        self._library_size = None

        self.create_db()
        self.scan_libraries()

    def create_db(self):
        if os.path.isfile(self.db_file):
            logger.debug('Library file ({}) exists and will be removed'.format(self.db_file))
            os.remove(self.db_file)
        else:
            logger.debug('Library file ({}) does not exist and will be created'.format(self.db_file))

        with OpenConnection(self.db_file) as db:
            db.execute(CREATE_LIBRARY)

    def scan_libraries(self):
        logger.debug('Scanning following directory(s):{}'.format('\n\t'.join(self.dirs)))

        for loc_raw in self.dirs:
            loc = os.path.expanduser(loc_raw)
            logger.debug('Scanning {raw}, expanded to {expanded}'.format(raw=loc_raw, expanded=loc))

            for (dirpath, _, filename) in os.walk(loc):
                if filename:
                    for f in filename:
                        if os.path.splitext(f)[1].lower() != '.mp3':
                            logger.info('Found non-mp3 file: {}'.format(f))
                            continue

                        self.adder.add(os.path.join(dirpath, f))

        with OpenConnection(self.db_file) as db:
            self._library_size = db.execute('SELECT count(*) FROM library;').fetchone()[0]

        logger.info('{} music files added'.format(self._library_size))
