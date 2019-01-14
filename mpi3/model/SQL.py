#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
INSERT OR IGNORE INTO library 
  (filepath, length, title, sortable_title, album, artist, track_number, total_tracks) 
VALUES (?,?,?,?,?,?,?,?);
'''

GET_PLAYLIST = '''
SELECT id 
FROM library
{filter_statement} 
ORDER BY {order_by}
{limit_clause}
{offset_clause}
;'''

GET_BY_ID = '''
SELECT id, {get_type}
FROM library
WHERE id IN ({param_count})
{limit_clause}
;'''

GET_COUNT = '''
SELECT COUNT(*)
FROM library
{filter_statement}
;'''

CREATE_ALBUMS = '''
CREATE TABLE albums (
      id    INTEGER PRIMARY KEY AUTOINCREMENT
    , album TEXT
);'''

INSERT_ALBUMS = '''
INSERT INTO albums (album)
SELECT album 
FROM library
WHERE 
    album IS NOT NULL
    AND album != ''
GROUP BY album
ORDER BY album
;'''

CREATE_ARTISTS = '''
CREATE TABLE artists (
      id     INTEGER PRIMARY KEY AUTOINCREMENT
    , artist TEXT
);'''

INSERT_ARTISTS = '''
INSERT INTO artists (artist)
SELECT artist
FROM library
WHERE 
    artist IS NOT NULL
    AND artist != ''
GROUP BY artist
ORDER BY artist
;'''

