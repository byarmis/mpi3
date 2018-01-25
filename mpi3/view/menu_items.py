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
    def __init__(self, draw, font, text, font_color):
        super(Button, self).__init__(draw, font, text, font_color)
        self.draw = draw
        self.font = font
        self.text = text
        self.font_color = font_color

    def __repr__(self):
        return 'BUTTON: {}'.format(self.text)

    def __str__(self):
        return self.text

    def render(self, offset):
        self.draw.text((0, offset), ' ' + str(self), font=self.font, fill=self.font_color)

    def on_click(self):
        pass


class SongButton(Button):
    def __init__(self, draw, font, text, font_color, song_id, play_song, transfer_func):
        super(SongButton, self).__init__(draw, font, text, font_color)
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
    def __init__(self, draw, font, text, font_color, button_type):
        super(MenuButton, self).__init__(draw, font, text, font_color)
        self.button_type = button_type

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
    def __init__(self, config, draw, font):
        super(Cursor, self).__init__()
        self.tfont_size = config['font']['title_size']
        self.font_size = config['font']['size']
        self.BLACK = get_color(config, black=True)

        self.draw = draw
        self.font = font

        self.value = 1

    def y(self):
        return self.tfont_size + (self.font_size * self.value)

    def render(self):
        self.draw.text((0, self.y), str(self), font=self.font, fill=self.BLACK)

    @property
    def y(self):
        logger.debug('Rendering cursor')
        logger.debug('\tvalue:{}'.format(self.value))
        logger.debug('\tfont size:{}'.format(self.font_size))
        logger.debug('\ttfont size{}'.format(self.tfont_size))
        y = (self.value * self.font_size) + self.tfont_size
        logger.debug('\ty value:{}'.format(y))
        return y

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
    def __init__(self, config, state, vol, draw, font):
        super(Title, self).__init__()
        self.state = state
        self.vol = vol

        self.draw = draw
        self.font = font
        self.BLACK = get_color(config, black=True)

    @property
    def time(self):
        return dt.now().strftime('%I:%M')

    def __str__(self):
        return '{state}   {time}  {vol}'.format(state=self.state,
                                                time=self.time,
                                                vol=self.vol)

    def render(self):
        logger.debug('Rendering title')
        self.draw.text((0, 0), str(self), font=self.font, fill=self.BLACK)

    def __repr__(self):
        return 'TITLE'
