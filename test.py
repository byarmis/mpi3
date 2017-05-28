import random
import time
import datetime
import string
from PIL import Image, ImageDraw, ImageFont
from papirus import Papirus

WHITE = 1
SCREEN_SIZE = (96, 200)
FONT_SIZE = 15
TITLE_SIZE = 13
PAGE_SIZE=11


def get_triple_letters():
    return ' '+''.join([random.choice(string.ascii_lowercase),
                        random.choice(string.ascii_lowercase),
                        random.choice(string.ascii_lowercase)])

def get_chunks(L):
    for i in range(0, len(L), PAGE_SIZE):
        yield L[i:i+PAGE_SIZE]

class Menu:
    def __init__(self):
        items = [get_triple_letters() for _ in range(30)] 
        self.paginated = [p for p in get_chunks(items)]
        self.page = 0
        self.cursor = 1

        self.papirus = Papirus(rotation=90)
        self.papirus.clear()

        self.update_partial = True

        self._image = Image.new('1', SCREEN_SIZE, WHITE)
        self._draw = ImageDraw.Draw(self._image)
        self._font = ImageFont.truetype('/home/pi/UbuntuMono-R.ttf', FONT_SIZE)
        self._title_font = ImageFont.truetype('/home/pi/UbuntuMono-R.ttf', TITLE_SIZE)
    
    def blank(self):
        self._draw.rectangle((0, 0) + SCREEN_SIZE, fill=WHITE, outline=WHITE)

    def title(self):
        return "X   12:45   {}".format(self.cursor)

    def draw_title(self):
        self._draw.text((0, 0), self.title(), font=self._title_font, fill=0)
        self._draw.text((0, TITLE_SIZE), '     <-', font=self._font, fill=0)

    def draw_cursor(self):
        y = TITLE_SIZE+(FONT_SIZE*self.cursor)
        self._draw.text((0, y), '>', font=self._font, fill=0)

    def get_coordinates(self, x):
        return (0, (FONT_SIZE*x)+TITLE_SIZE+FONT_SIZE)
    
    def draw_page(self):
        for loc, L in enumerate(self.paginated[self.page]):
            self._draw.text(self.get_coordinates(loc), L, font=self._font, fill=0)
    
    def update(self):
        if self.update_partial:
            self.papirus.partial_update()
        else:
            self.papirus.update()
            self.update_partial = True

    def render(self):
        self.blank()
        self.draw_title()
        self.draw_cursor()
        self.draw_page()
        self.papirus.display(self._image)
        self.update()

    def cursor_down(self):
        self.cursor += 1
        if self.cursor > PAGE_SIZE:
            self.cursor = 1
            self.page_next()
        
        if self.cursor > len(self.paginated[self.page]):
            self.cursor = 1
            self.page_next()

    def page_next(self):
        self.page += 1
        if self.page == len(self.paginated):
            self.page = 0 # Wrap around
        self.update_partial = False

m = Menu()
m.render()
time.sleep(1)

while True:
    m.cursor_down()
    m.render()
    time.sleep(1)
