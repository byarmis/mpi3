#!/bin/python

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
FROM library {filter_statement} 
ORDER BY {order_by}
{limit_clause}
{offset_clause}
;'''

GET_BY_ID = '''
SELECT id, {get_type}
FROM library
WHERE id IN (?)
{limit_clause}
;'''

GET_COUNT = '''
SELECT COUNT(*)
FROM library {filter_statement}
;'''

