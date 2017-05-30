#!/bin/python
from PIL import Image, ImageDraw, ImageFont
from subprocess import check_output, call
import datetime
import random
import re
import string
import time

from papirus import Papirus

WHITE = 1
BLACK = 0
FONT_SIZE = 15
TITLE_SIZE = 13
PAGE_SIZE=11
SCREEN_SIZE = (96, 200)


FONT = '/home/pi/UbuntuMono-R.ttf'

def get_triple_letters():
    return ' '+''.join([random.choice(string.ascii_lowercase),
                        random.choice(string.ascii_lowercase),
                        random.choice(string.ascii_lowercase)])

def get_chunks(L):
    for i in range(0, len(L), PAGE_SIZE):
        yield L[i:i+PAGE_SIZE]

def get_font_draw(image, size=FONT_SIZE):
    font = ImageFont.truetype(FONT, size)
    draw = ImageDraw.Draw(image)
    return (font, draw)

class Cursor:
    def _get_y(self):
        return TITLE_SIZE + (FONT_SIZE * self.value)

    def __init__(self, image, size=15):
        self.value = 1
        self.y = self._get_y()

        self.image = image
        self.font, self.draw = get_font_draw(image, size)

    def draw_cursor(self):
        self.y = self._get_y()
        self.draw.text((0, self.y), '>', font=self.font, fill=BLACK)

class State:
    def __init__(self):
        self.icons = {'normal': ' ',
                      'shuffle': 'X',
                      'repeat one': 'o',
                      'repeat all': 'O'}
        self.state_names = ('normal', 'shuffle', 'repeat one', 'repeat all')
        self.cnt = 0
        self.state = self.get()

    def get(self):
        return self.state_names[self.cnt]

    def next(self):
        self.state_cnt += 1
        self.state_cnt %= len(self.state_names)

        self.state = self.get()

    def __str__(self):
        return self.icons[self.state]


class Title:
    def __init__(self, image, state, volume):
        self.font, self.draw = get_font_draw(image, TITLE_SIZE)
        self.state = state
        self.volume = volume

    @property
    def state(self):
        return str(self.state)

    @property
    def time(self):
        return datetime.datetime.now().strftime('%I:%M')

    def get_text(self):
        return '{state}   {time}   {volume}'.format(state=self.state, 
                                                    time=self.time,
                                                    volume=self.volume.get)

    def draw_title(self):
        self.draw.text((0,0), self.get_text(), font=self.font)

class Volume:
    def __init__(self):
        self.val = 1
        _ = self.set_volume(self.val)

    @property
    def increase(self):
        if self.val < 19:
            self.val += 1

        _ = self.set_volume(self.val)

    @property
    def decrease(self):
        if self.val > 1:
            self.val -= 1

        _ = self.set_volume(self.val)

    def set_volume(self, val):
        return call(['amixer', 'sset', 'Master', '{}%'.format(self.get)])

    @property
    def get(self):
        return self.val * 5


class BackButton:
    def __init__(self, text, image):
        self.text = text

        self.font, self.draw = get_font_draw(image)

    def __repr__(self):
        return self.text
    def __str__(self):
        return self.text

    def on_press(self):
        raise NotImplementedError

    def draw_button(self):
        self.draw.text((0, TITLE_SIZE), self.text, font=self.font)

class Player:
    def __init__(self, font=FONT):
        self.font = font

        self.papirus = Papirus(rotation=90)

        self.image = Image.new('1', SCREEN_SIZE, WHITE)
        self.draw = ImageDraw.Draw(self.image)
        
        self.vol = Volume()
        self.cursor = Cursor(self.image)
        self.screen = Screen(self, self.papirus)
        self.menu = Menu(self.image)
        self.back = BackButton('   <-', self.image)
        self.state = State()
        self.title = Title(self.image, state=self.state, volume=self.vol)

    def move_cursor(self, dir):
        self.cursor.value += dir

        if self.cursor.value < 0:
            self.cursor.value = 1
            self.page_change(-1)

        elif self.cursor.value > min((PAGE_SIZE, len(self.menu.page))):
            self.cursor.value = 1
            self.page_change(1)

    def page_change(self, dir):
        self.menu.page_val += dir
        if self.menu.page_val == len(self.menu.paginated):
            self.menu.page_val = 0 # Wrap around

        elif self.menu.page_val < 0:
            self.menu.page_val = len(self.menu.paginated) - 1

        self.screen.update_partial = False

class Screen:
    def __init__(self, player, papirus, size=SCREEN_SIZE):
        self.player = player
        self.size = size
        self.update_partial = False

        self.image = player.image
        self.draw = ImageDraw.Draw(self.image)
        self.papirus = papirus

        self.papirus.clear()

    def render(self):
        self.blank()
        self.player.title.draw_title()
        self.player.back.draw_button()
        self.player.cursor.draw_cursor()
        self.player.menu.draw_page()

        self.papirus.display(self.image)
        self.update()
 
    def update(self):
        if self.update_partial:
            self.papirus.partial_update()
        else:
            self.papirus.update()
            self.update_partial = True

    def blank(self):
        self.draw.rectangle((0, 0) + self.size, fill=WHITE, outline=WHITE)


class Menu:
    def __init__(self, image, font=FONT):
        self.image = image
        self.draw = ImageDraw.Draw(self.image)
        self.font = ImageFont.truetype(font, FONT_SIZE)

        items = [get_triple_letters() for _ in range(30)] 
        self.paginated = [p for p in get_chunks(items)]
        self.page_val = 0

    @property
    def page(self):
        return self.paginated[self.page_val]

    def get_coordinates(self, x):
        # Title plus back button
        offset = TITLE_SIZE + FONT_SIZE
        return (0, (FONT_SIZE*x)+offset)
    
    def draw_page(self):
        for loc, L in enumerate(self.page):
            self.draw.text(self.get_coordinates(loc), L, font=self.font, fill=BLACK)

DELAY = 0.5
p = Player()
p.screen.render()
time.sleep(DELAY)

while True:

    for _ in range(18):
        p.vol.increase
        print p.vol.get

    for _ in range(18):
        p.vol.decrease
        print p.vol.get
