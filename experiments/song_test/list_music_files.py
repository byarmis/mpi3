import os

path = os.path.expanduser('~/Music/')
valid_files = ('mp3','ogg')

for root, dirs, files in os.walk(path):
    for file in files:
        if file and file.lower().endswith(valid_files):
            print os.path.join(root, file)

