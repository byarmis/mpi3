#!/bin/python3
from PIL import Image, ImageDraw, ImageFont
from subprocess import call
from itertools import cycle
import os
import datetime
import random
import string
import time

from initialize import get_config, scan_library

# TODO: Add conditional import or mock
if False:
    from papirus import Papirus
else:
    from tests.PapirusMock import PapirusMock as Papirus


def get_triple_letters():
    return ' ' + ''.join([random.choice(string.ascii_lowercase),
                          random.choice(string.ascii_lowercase),
                          random.choice(string.ascii_lowercase)])


class Cursor:
    def _get_y(self):
        return self.player.config['font']['title_size'] + (self.player.config['font']['size'] * self.value)

    def __init__(self, player):
        self.player = player

        self.value = 1
        self.y = self._get_y()

        self.image = player.image
        self.font = player.font
        self.draw = player.draw

    def draw_cursor(self):
        self.y = self._get_y()
        self.draw.text((0, self.y), '>', font=self.font, fill=self.player.BLACK)


class State:
    def __init__(self):
        self.icons = {'normal': ' ',
                      'shuffle': 'X',
                      'repeat one': 'o',
                      'repeat all': 'O'}
        self.state_names = cycle(('normal', 'shuffle', 'repeat one', 'repeat all'))
        self.state = next(self.state_names)

    def next(self):
        self.state = next(self.state_names)

    def __str__(self):
        return self.icons[self.state]


class Title:
    def __init__(self, player):
        self.player = player

    @property
    def state(self):
        return str(self.player.state)

    @property
    def time(self):
        return datetime.datetime.now().strftime('%I:%M')

    def get_text(self):
        return f'{self.player.state}   {self.time}   {self.player.vol.get}'

    def draw_title(self):
        self.player.draw.text((0, 0), self.get_text(), font=self.player.font)


class Volume:
    def __init__(self):
        self.val = 1
        self.set_volume(self.val)

    @property
    def increase(self):
        if self.val < 19:
            self.val += 1
        self.set_volume(self.val)

    @property
    def decrease(self):
        if self.val > 1:
            self.val -= 1
        self.set_volume(self.val)

    @property
    def get(self):
        return self.val * 5

    def set_volume(self, val):
        self.val = val
        call(['amixer', 'sset', 'Master', '{}%'.format(self.get)])


class Button:
    def __init__(self, player, text, on_press=None, args=None, kwargs=None):
        self.text = text
        self.player = player
        self.f = on_press

        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        return self.text

    def __str__(self):
        return self.text

    def on_press(self):
        if self.f:
            self.f(*self.args, **self.kwargs)


class Library:
    def __init__(self, player):
        self.player = player
        self.items = []
        for loc in player.config['music']['directory']:
            self.items.append(scan_library(loc))


class Player:
    def __init__(self, menu=None):
        self.config = get_config()
        self.screen_size = (self.config['screen_size']['width'],
                            self.config['screen_size']['height'])

        self.WHITE = self.config['colors']['white']
        self.BLACK = self.config['colors']['black']

        self.font = ImageFont.truetype(self.config['font']['dir'], self.config['font']['size'])
        self.papirus = Papirus(rotation=90)
        self.image = Image.new('1', self.screen_size, self.WHITE)
        self.draw = ImageDraw.Draw(self.image)

        self.vol = Volume()
        self.cursor = Cursor(self)
        self.screen = Screen(self)
        self.menu = menu or Menu(self)
        self.back = Button(self, text='   <-', on_press=self.menu.previous)
        self.state = State()
        self.title = Title(self)
        self.library = Library(self)

        self.home = True

    def move_cursor(self, direction):
        self.cursor.value += direction

        if self.cursor.value < 0:
            self.cursor.value = 1
            self.page_change(-1)

        elif self.cursor.value > min((self.config['computed']['page_size'], len(self.menu.page))):
            self.cursor.value = 1
            self.page_change(1)

    def page_change(self, direction):
        self.menu.page_val += direction
        if self.menu.page_val == len(self.menu.paginated):
            self.menu.page_val = 0  # Wrap around

        elif self.menu.page_val < 0:
            self.menu.page_val = len(self.menu.paginated) - 1

        self.screen.update_partial = False


class Screen:
    def __init__(self, player):
        self.player = player
        self.size = player.screen_size
        self.update_partial = False

        self.player.papirus.clear()

    def render(self):
        self.blank()
        self.player.title.draw_title()

        if not self.player.home:
            self.player.draw.text((0, self.player.config['font']['title_size']),
                                  self.player.back, font=self.player.font)

        self.player.cursor.draw_cursor()
        self.player.menu.draw_page()

        self.player.papirus.display(self.player.image)
        self.update()

    def update(self):
        if self.update_partial:
            self.player.papirus.partial_update()
        else:
            self.player.papirus.update()
            self.update_partial = True

    def blank(self):
        self.player.draw.rectangle((0, 0) + self.size, fill=self.player.WHITE, outline=self.player.WHITE)


class Menu:
    def __init__(self, player):
        self.player = player

        items = [get_triple_letters() for _ in range(30)]
        self.paginated = [p for p in self.get_pages(items)]
        self.page_val = 0

    def previous(self):
        print('Going to previous')

    def get_child(self):
        self.player.home = False
        # Get the item in the list selected by the cursor
        print(self.paginated[self.page_val][self.player.cursor.value])

    def get_pages(self, L):
        for i in range(0, len(L), self.player.config['computed']['page_size']):
            yield L[i:i + self.player.config['computed']['page_size']]

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


