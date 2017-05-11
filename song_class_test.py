import os
from mutagen.easyid3 import EasyID3 as ID3

path = os.path.expanduser('~/Music/')
valid_files = ('mp3','ogg')

MAX_LEN = 10

class Song:
    def __init__(self, path, name=None):
        self.path = path
        self.name = name or os.path.basename(path)

        self.id3 = ID3(self.path)

    def __repr__(self):
        return self.path
    def __str__(self):
        return self.name

    @property
    def short_name(self):
        return self.id3['title'][0][:MAX_LEN] or self.name[:MAX_LEN] 

    @property
    def artist(self):
        return self.id3['artist'][0] or None


for root, dirs, files in os.walk(path):
    for file in files:
        if file and file.lower().endswith(valid_files):
            s = Song(path=os.path.join(root, file), name=None)

            print '{}\t{}'.format(s.short_name, s.artist)

