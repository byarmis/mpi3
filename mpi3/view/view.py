#!/bin/python
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime as dt
from abc import ABCMeta, abstractmethod
import logging

from papirus import Papirus
from mpi3.model.constants import CURSOR_DIR

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# TODO: Create decorator that triggers a redraw after function is called
# Have to make sure that if multiple functions are called that trigger a 
# redraw after they're done, there's only one resulting redraw

# TODO: ABC for menu item.  Must implement `render` method

# View: Everything dealing with stuff on the screen
# Screen: What's on the screen at the moment
# Menu: What can be shown on the screen by scrolling up / down and what happens on interaction
# Button: A line item on the screen that can be clicked 
# Not necessary to be  clicked-- informational buttons that just show info without doing anything on click.
# Maybe even skip over them in navigation.  Show with italics?
# Menu structure: The parent / children menus of the current menu--
# can be done dynamically without having to pre-generate everything

class ViewItem(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def render(self, *args):
        pass


def _get_color(config, black=False, white=False):
    if black:
        return config['colors']['black']
    elif white:
        return config['colors']['white']
    else:
        raise ValueError('Pick either black or white')


def _get_screen_size(config):
    return config['screen_size']['width'], config['screen_size']['height']


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
            pass
        elif self.button_type == 'ARTIST':
            # Show the artist
            pass
        elif self.button_type == 'MENU':
            # Go into the menu
            pass


class Renderer(object):
    def __init__(self, draw, image, config, targets, papirus):
        self.draw = draw
        self.image = image
        self.size = _get_screen_size(config)
        self.WHITE = _get_color(config=config, white=True)
        self.targets = targets
        self.papirus = papirus

        self.partial_update = False

    def render(self):
        self.blank()
        logger.debug('Rendering')
        for t in self.targets:
            logger.debug('\t{}'.format(repr(t)))
            t.render()

        self.papirus.display(self.image)

        self.update()

    def blank(self):
        logger.debug('Blanking')
        self.draw.rectangle((0, 0) + self.size, fill=self.WHITE, outline=self.WHITE)

    def update(self):
        logger.debug('Updating')
        if self.partial_update:
            self.papirus.partial_update()
        else:
            self.papirus.update()
            self.partial_update = True


class View(object):
    def __init__(self, playback_state, volume, config, play_song, transfer_func):
        self.config = config

        self.screen_size = _get_screen_size(config)

        self.title_font = self._get_font(self.config['font']['dir'], self.config['font']['title_size'])
        self.font = self._get_font(self.config['font']['dir'], self.config['font']['size'])

        self.WHITE = _get_color(config, white=True)
        self.BLACK = _get_color(config, black=True)

        self.papirus = Papirus(rotation=90)
        self.papirus.clear()

        self.image = Image.new('1', self.screen_size, self.WHITE)
        self.draw = ImageDraw.Draw(self.image)
        self._play_song = play_song
        self._transfer_func = transfer_func

        self._title = Title(config=config, state=playback_state, vol=volume, draw=self.draw, font=self.title_font)
        self._cursor = Cursor(config, draw=self.draw, font=self.font)

        self.renderer = Renderer(image=self.image, draw=self.draw,
                                 config=config, papirus=self.papirus,
                                 targets=[
                                     self._cursor,
                                     self._title
                                 ])

        self._cursor.set_rendering_engine(self.renderer)

    @staticmethod
    def _get_font(font_dir, font_size):
        return ImageFont.truetype(os.path.expanduser(font_dir), font_size)


class Cursor(ViewItem):
    def __init__(self, config, draw, font):
        super(Cursor, self).__init__()
        self.tfont_size = config['font']['title_size']
        self.font_size = config['font']['size']
        self.BLACK = _get_color(config, black=True)

        self.draw = draw
        self.font = font

        self.value = 1
        self.y = self._get_y()
        self.rendering_engine = None

    def _get_y(self):
        return self.tfont_size + (self.font_size * self.value)

    def set_rendering_engine(self, renderer):
        self.rendering_engine = renderer

    def render(self):
        self.y = self._get_y()
        self.draw.text((0, self.y), str(self), font=self.font, fill=self.BLACK)

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

        self.rendering_engine.render()


class Title(ViewItem):
    def __init__(self, config, state, vol, draw, font):
        super(Title, self).__init__()
        self.state = state
        self.vol = vol

        self.draw = draw
        self.font = font
        self.BLACK = _get_color(config, black=True)

    @property
    def time(self):
        return dt.now().strftime('%I:%M')

    def __str__(self):
        return '{state}   {time}   {vol}'.format(state=self.state,
                                                 time=self.time,
                                                 vol=self.vol)

    def render(self):
        logger.debug('Rendering title')
        self.draw.text((0, 0), str(self), font=self.font, fill=self.BLACK)

    def __repr__(self):
        return 'TITLE'

# class Screen:
#     def __init__(self, player):
#         self.player = player
#         self.size = player.screen_size
#         self.update_partial = False
#
#         self.player.papirus.clear()
#
#     def render(self):
#         self.blank()
#         self.player.title.draw_title()
#
#         self.cursor.draw_cursor()
#         self.menu.draw_page()
#
#         self.player.papirus.display(self.player.image)
#         self.update()
#
#     def update(self):
#         if self.update_partial:
#             self.player.papirus.partial_update()
#         else:
#             self.player.papirus.update()
#             self.update_partial = True
#
#     def blank(self):
#         self.player.draw.rectangle((0, 0) + self.size,
#                                    fill=self.player.WHITE,
#                                    outline=self.player.WHITE)
#
#
# class Menu:
#     def __init__(self, player, items, parent=None):
#         self.items = items
#         self.page_size = player.config['computed']['page_size']
#         self.player = player
#         self.paginated = [p for p in self.generate_pages()]
#         self.page_val = 0
#         self.parent = parent
#
#     def previous(self):
#         print('Going to previous')
#         return self.parent
#
#     def get_child(self, val):
#         # Get the item in the list selected by the cursor
#         print(self.paginated[self.page_val][val])
#
#     def generate_pages(self):
#         for i in range(0, len(self.items), self.page_size):
#             yield self.items[i:i + self.page_size]
#
#     @property
#     def page(self):
#         return self.paginated[self.page_val]
#
#     def get_coordinates(self, x):
#         # Title plus back button
#         font_size = self.player.config['font']['size']
#         offset = self.player.config['font']['title_size'] + font_size
#         return 0, (font_size * x) + offset
#
#     def draw_page(self):
#         for loc, L in enumerate(self.page):
#             self.player.draw.text(self.get_coordinates(loc), L, font=self.player.font, fill=self.player.BLACK)
