#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import subprocess

logger = logging.getLogger(__name__)


class Button:
    # A line item on the screen that can optionally be clicked
    def __init__(self, text, on_click=None):
        self.text = text
        self._on_click = on_click

    def __repr__(self):
        return 'BUTTON: {}'.format(self.text)

    def __str__(self):
        return self.text

    def button_type(self):
        return 'BUTTON'

    def on_click(self):
        if self._on_click is not None:
            self._on_click()


class ShellButton(Button):
    def __init__(self, text, directory, shell_script):
        if not directory.endswith('/'):
            directory += '/'
        shell_script = os.path.expanduser(directory + shell_script)

        func = lambda: subprocess.call(['sudo ' + shell_script], shell=True)
        super(ShellButton, self).__init__(text=text, on_click=func)

    def button_type(self):
        return 'SHELL'


class SongButton(Button):
    # A button that's a song
    def __init__(self, song_title, song_path, play_song):
        self.song_title = song_title
        self.song_path = song_path

        func = lambda: play_song(song_path)
        super(SongButton, self).__init__(text=song_title, on_click=func)

    def button_type(self):
        return 'SONG'


class MenuButton(Button):
    def __init__(self, menu_type, text):
        super(MenuButton, self).__init__(text=text)
        self.menu_type = menu_type

    def __str__(self):
        return self.text

    def button_type(self):
        return 'MENU'

    def on_click(self):
        if self.menu_type == 'ALBUM':
            # Show the album
            # Generate the sub menu?
            # return Menu()
            pass
        elif self.menu_type == 'ARTIST':
            # Show the artist
            pass
        elif self.menu_type == 'MENU':
            # Go into the menu
            # Add current menu to menu stack
            # Selected menu is now current menu
            # Rerender
            pass
