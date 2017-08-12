#!/bin/python

import sqlite3
import logging
import os
import mutagen # TODO: ADD

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

CREATE_LIBRARY = '''
CREATE TABLE library (
      id            INTEGER PRIMARY KEY AUTOINCREMENT
    , filepath      TEXT UNIQUE NOT NULL
    , length        INTEGER
    , album         TEXT
    , artist        TEXT
    , disc          INTEGER
    , track_number  INTEGER
);
'''

INSERT_SONGS = '''
INSERT INTO library 
  (filepath, length, album, artist, disc, track_number) 
VALUES {};
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
# (filepath, length, album, artist, disc, track_number)

        return (f,)

    def _add_buffer(self):
        values_str = ','.join(str(i) for i in self._buffer)
        with OpenConnection(self.db_file) as db:
            db.execute(INSERT_SONGS.format(values_str))

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
            self._library_size = db.execute('SELECT count(*) FROM library;').fetchall()

        logger.info('{} music files added'.format(self._library_size))
