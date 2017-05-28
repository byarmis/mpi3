import random
import time
import datetime
import string
from PIL import Image, ImageDraw, ImageFont
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

class Title:
    def __init__(self, image):
        self.font, self.draw = get_font_draw(image, TITLE_SIZE)

    @property
    def state(self):
        return 'X'

    @property
    def time(self):
        return '12:54'

    @property
    def volume(self):
        return '5'

    def get_text(self):
        return '{state}   {time}   {volume}'.format(state=self.state, time=self.time, volume=self.volume)

    def draw_title(self):
        self.draw.text((0,0), self.get_text(), font=self.font)

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
        
        self.cursor = Cursor(self.image)
        self.title = Title(self.image)
        self.screen = Screen(self, self.papirus)
        self.menu = Menu(self.image)
        self.back = BackButton('   <-', self.image)

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
    for _ in range(40):
        p.move_cursor(1)
        p.screen.render()
        time.sleep(DELAY)

    for _ in range(40):
        p.move_cursor(-1)
        p.screen.render()
        time.sleep(DELAY)
