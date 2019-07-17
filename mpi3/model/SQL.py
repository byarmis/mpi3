#!/usr/bin/env python3
# -*- coding: utf-8 -*-

create_library = '''
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
)
;'''

create_view_list = '''
CREATE TABLE viewlist (
      id  INTEGER PRIMARY KEY 
    , txt TEXT
)
;'''

create_play_list = '''
CREATE TABLE playlist (
    id INTEGER PRIMARY KEY
)
;'''

CREATE_STATEMENTS = [
    ('library', create_library)
    , ('viewlist', create_view_list)
    , ('playlist', create_play_list)
]

INSERT_SONGS = '''
INSERT OR IGNORE INTO library 
  (filepath, length, title, sortable_title, album, artist, track_number, total_tracks) 
VALUES (?,?,?,?,?,?,?,?)
;'''

GET_VIEW_LIST = '''
SELECT 
    id
  , txt
FROM 
    viewlist
{limit_clause}
{offset_clause}
;'''

INSERT_VIEW_LIST = '''
INSERT INTO viewlist (id, txt)
SELECT
    id
  , {col}
FROM library
{filter_clause}
ORDER BY
    {order_clause}
;'''

INSERT_PLAYLIST = '''
INSERT INTO playlist (id)
SELECT id
FROM viewlist
ORDER BY 
    {order_clause}
;'''

TRUNCATE_TABLE = '''
DELETE FROM {table}
;'''

VIEW_LIST_TO_PLAYLIST = '''
INSERT INTO playlist (id)
SELECT id
FROM viewlist
{offset_clause}
{limit_clause}
;'''

GET_PLAYLIST = '''
SELECT id 
FROM playlist
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
FROM {table}
{filter_statement}
;'''
