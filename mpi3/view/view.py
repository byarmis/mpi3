#!/bin/python
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime as dt

from papirus import Papirus


class View(object):
    def __init__(self, playback_state, volume, config):
        self.config = config
        self.playback_state = playback_state
        self.vol = volume

        self.screen_size = (self.config['screen_size']['width'],
                            self.config['screen_size']['height'])

        # TODO: Change \/ ?
        self.title_font = ImageFont.truetype(os.path.expanduser(self.config['font']['dir']),
                                             self.config['font']['title_size'])
        self.font = ImageFont.truetype(os.path.expanduser(self.config['font']['dir']),
                                       self.config['font']['size'])

        self.WHITE = self.config['colors']['white']
        self.BLACK = self.config['colors']['black']

        self.papirus = Papirus(rotation=90)
        self.image = Image.new('1', self.screen_size, self.WHITE)
        self.draw = ImageDraw.Draw(self.image)

        self.cursor = Cursor(config, draw=self.draw, font=self.font)


class Cursor:
    def __init__(self, config, draw, font):
        self.tfont_size = config['font']['title_size']
        self.font_size = config['font']['size']
        self.BLACK = config['colors']['black']

        self.draw = draw
        self.font = font

        self.value = 1
        self.y = self._get_y()

    def _get_y(self):
        return self.tfont_size + (self.font_size * self.value)

    def draw_cursor(self):
        self.y = self._get_y()
        self.draw.text((0, self.y), '>', font=self.font, fill=self.BLACK)

    def move_cursor(self, direction, reset=False):
        if reset:
            self.value = 1
        else:
            self.value += direction


class Title(object):
    def __init__(self, state, vol, draw, font):
        self.state = state
        self.vol = vol

        self.draw = draw
        self.font = font

    @property
    def time(self):
        return dt.now().strftime('%I:%M')

    def __str__(self):
        return '{state}   {time}   {vol}'.format(state=self.state,
                                                 time=self.time,
                                                 vol=self.vol)

    def draw_title(self):
        self.draw.text((0, 0), str(self), font=self.font)


class Screen:
    def __init__(self, player):
        self.player = player
        self.size = player.screen_size
        self.update_partial = False

        self.player.papirus.clear()

    def render(self):
        self.blank()
        self.player.title.draw_title()

        self.cursor.draw_cursor()
        self.menu.draw_page()

        self.player.papirus.display(self.player.image)
        self.update()

    def update(self):
        if self.update_partial:
            self.player.papirus.partial_update()
        else:
            self.player.papirus.update()
            self.update_partial = True

    def blank(self):
        self.player.draw.rectangle((0, 0) + self.size,
                                   fill=self.player.WHITE,
                                   outline=self.player.WHITE)


class Menu:
    def __init__(self, player, items, parent=None):
        self.items = items
        self.page_size = player.config['computed']['page_size']
        self.player = player
        self.paginated = [p for p in self.generate_pages()]
        self.page_val = 0
        self.parent = parent

    def previous(self):
        print('Going to previous')
        return self.parent

    def get_child(self, val):
        # Get the item in the list selected by the cursor
        print(self.paginated[self.page_val][val])

    def generate_pages(self):
        for i in range(0, len(self.items), self.page_size):
            yield self.items[i:i + self.page_size]

    @property
    def page(self):
        return self.paginated[self.page_val]

    def get_coordinates(self, x):
        # Title plus back button
        font_size = self.player.config['font']['size']
        offset = self.player.config['font']['title_size'] + font_size
        return 0, (font_size * x) + offset

    def draw_page(self):
        for loc, L in enumerate(self.page):
            self.player.draw.text(self.get_coordinates(loc), L, font=self.player.font, fill=self.player.BLACK)
