#!/bin/python
from abc import ABCMeta, abstractmethod
import logging
from datetime import datetime as dt

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class ViewItem(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def __str__(self):
        pass


class Button(ViewItem):
    # A line item on the screen that can optionally be clicked
    def __init__(self, text, on_click=None):
        super(Button, self).__init__()
        self.text = text
        self._on_click = on_click

    def __repr__(self):
        return 'BUTTON: {}'.format(self.text)

    def __str__(self):
        return self.text

    def on_click(self):
        if self._on_click is not None:
            self._on_click()


class SongButton(Button):
    def __init__(self, song_id, song_title, play_song, transfer_func):
        super(SongButton, self).__init__()
        self.button_type = 'SONG'
        self.play_song = play_song
        self.song_id = song_id
        self.song_title = song_title
        self.transfer_lists = transfer_func

    def __repr__(self):
        return 'SONG BUTTON: {}'.format(self.song_title)

    def on_click(self):
        # Play by song ID
        self.play_song(self.song_id)

        # Set the view list to be the play list
        self.transfer_lists()


class MenuButton(Button):
    def __init__(self, button_type, text):
        super(MenuButton, self).__init__()
        self.button_type = button_type
        self.text = text

    def __str__(self):
        return self.text

    def on_click(self):
        if self.button_type == 'ALBUM':
            # Show the album
            # Generate the sub menu?
            pass
        elif self.button_type == 'ARTIST':
            # Show the artist
            pass
        elif self.button_type == 'MENU':
            # Go into the menu
            # Add current menu to menu stack
            # Selected menu is now current menu
            # Rerender
            pass


class Cursor(ViewItem):
    def __init__(self):
        super(Cursor, self).__init__()

        self.value = 1

    def __repr__(self):
        return 'CURSOR'

    def __str__(self):
        return '>'

    def move(self, direction=None, reset=False):
        if reset:
            self.value = 1
        elif direction:
            self.value += direction
        else:
            raise ValueError('Must pass either reset (T/F) or direction')


class Title(ViewItem):
    def __init__(self, state, vol):
        super(Title, self).__init__()
        self.state = state
        self.vol = vol

    def __str__(self):
        return '{state}   {time}  {vol}'.format(state=self.state,
                                                time=self.time,
                                                vol=self.vol)

    def __repr__(self):
        return 'TITLE'

    @property
    def time(self):
        return dt.now().strftime('%I:%M')
