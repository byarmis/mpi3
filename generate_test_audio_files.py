#!/usr/bin/env python3

import argparse
import os
import random
import string

from gtts import gTTS
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3 as ID3


NUMBERS = [
        'zero'
        , 'one'
        , 'two'
        , 'three'
        , 'four'
        , 'five'
        , 'six'
        , 'seven'
        , 'eight'
        , 'nine'
]

def get_num_as_str(i):
    return ' '.join(NUMBERS[int(c)] for c in str(i))

def get_artist_album(i=None):
    return ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(1, 10)))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-of', '--output-folder', default='sound_files', type=str, dest='output_folder',
            help='The folder to output the created files to')

    parser.add_argument('-n', '--number', required=True, type=int, dest='cnt',
            help='The number of files to generate')

    parser.add_argument('-nart', '--number-artists', type=int, default=50, dest='artist_count',
            help='The number of random artists to generate')

    parser.add_argument('-nalb', '--number-albums', type=int, default=50, dest='album_count',
            help='The number of random albums to generate')

    args = parser.parse_args()

    artists = [get_artist_album() for _ in range(args.artist_count)]
    albums = [get_artist_album() for _ in range(args.album_count)]

    os.makedirs(args.output_folder, exist_ok=True)
    cur_dir = os.path.dirname(os.path.realpath(__file__))

    for i in range(args.cnt):
        print(i)

        filename = os.path.join(cur_dir, args.output_folder, '{}.mp3'.format(i))

        gTTS(get_num_as_str(i)).save(filename)

        audio = MP3(filename, ID3=ID3)
        audio['title'] = get_num_as_str(i)
        audio['artist'] = random.choice(artists)
        audio['album'] = random.choice(albums)
        audio.save()

