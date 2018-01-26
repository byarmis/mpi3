#!/bin/python
from abc import ABCMeta, abstractmethod
import logging
from datetime import datetime as dt

from utils import get_color

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class ViewItem(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def render(self, *args):
        pass


class Button(ViewItem):
    # A line item on the screen that can optionally be clicked
    def __init__(self, render_helper, text, on_click=None):
        super(Button, self).__init__()
        self.draw = render_helper.draw
        self.font = render_helper.font
        self.BLACK = render_helper.get_black()
        self.text = text
        self._on_click = on_click

    def __repr__(self):
        return 'BUTTON: {}'.format(self.text)

    def __str__(self):
        return self.text

    def render(self, offset):
        self.draw.text((0, offset), ' ' + str(self), font=self.font, fill=self.BLACK)

    def on_click(self):
        if self._on_click is not None:
            self._on_click()


class SongButton(Button):
    def __init__(self, render_helper, song_id, play_song, transfer_func):
        super(SongButton, self).__init__(render_helper)
        self.button_type = 'SONG'
        self.play_song = play_song
        self.song_id = song_id
        self.transfer_lists = transfer_func

    def on_click(self):
        # Play by song ID
        self.play_song(self.song_id)

        # Set the view list to be the play list
        self.transfer_lists()


class MenuButton(Button):
    def __init__(self, render_helper, button_type, text):
        super(MenuButton, self).__init__(render_helper, text)
        self.button_type = button_type
        self.text = text
        self.render_helper = render_helper

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
    def __init__(self, render_helper):
        super(Cursor, self).__init__()
        self._render_helper = render_helper

        self.tfont_size = render_helper.config['font']['title_size']
        self.font_size = render_helper.config['font']['size']
        self.BLACK = get_color(render_helper.config, black=True)

        self.value = 1

    @property
    def y(self):
        return self.tfont_size + (self.font_size * self.value)

    def render(self, _):
        self._render_helper.draw.text((0, self.y)
                                      , str(self)
                                      , font=self._render_helper.font
                                      , fill=self.BLACK)

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
    def __init__(self, render_helper, state, vol):
        super(Title, self).__init__()
        self.state = state
        self.vol = vol

        self.draw = render_helper.draw
        self.font = render_helper.tfont
        self.BLACK = render_helper.get_black()

    @property
    def time(self):
        return dt.now().strftime('%I:%M')

    def __str__(self):
        return '{state}   {time}  {vol}'.format(state=self.state,
                                                time=self.time,
                                                vol=self.vol)

    def render(self, _):
        logger.debug('Rendering title')
        self.draw.text((0, 0), str(self), font=self.font, fill=self.BLACK)

    def __repr__(self):
        return 'TITLE'
