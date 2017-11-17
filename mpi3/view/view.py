#!/bin/python
from PIL import Image, ImageDraw
import logging

from papirus import Papirus
from mpi3.model.constants import CURSOR_DIR
from utils import get_screen_size, get_color, get_font
from menu_items import Title, Cursor

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# View: Everything dealing with stuff on the screen
# Screen: What's on the screen at the moment
# Menu: What can be shown on the screen by scrolling up / down and what happens on interaction
# Button: A line item on the screen that can be clicked 
# Not necessary to be  clicked-- informational buttons that just show info without doing anything on click.
# Maybe even skip over them in navigation.  Show with italics?
# Menu structure: The parent / children menus of the current menu--
# can be done dynamically without having to pre-generate everything


class Renderer(object):
    def __init__(self, draw, image, config, targets, papirus):
        self.draw = draw
        self.image = image
        self.size = get_screen_size(config)
        self.WHITE = get_color(config=config, white=True)
        self.targets = targets
        self.papirus = papirus

        self.partial_update = False

    def render(self, partial=None):
        self.blank()
        logger.debug('Rendering')
        for t in self.targets:
            logger.debug('\t{}'.format(repr(t)))
            t.render()

        self.papirus.display(self.image)

        self.update(partial=partial)

    def blank(self):
        logger.debug('Blanking')
        self.draw.rectangle((0, 0) + self.size, fill=self.WHITE, outline=self.WHITE)

    def update(self, partial):
        logger.debug('Updating ({})'.format('partially' if self.partial_update else 'completely'))
        if self.partial_update or partial:
            self.papirus.partial_update()
        else:
            self.papirus.update()
            self.partial_update = True


class View(object):
    def __init__(self, playback_state, volume, config, play_song, transfer_func):
        self.config = config

        self.screen_size = get_screen_size(config)

        self.title_font = get_font(config, 'title_size')
        self.font = get_font(config, 'size')

        self.WHITE = get_color(config, white=True)
        self.BLACK = get_color(config, black=True)

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

    def move_cursor(self, direction=None, reset=False):
        # TODO: Flesh out with menu/screen changing (w/ cursor resetting) and all that fun stuff
        self._cursor.move(direction=direction, reset=reset)
        self.renderer.render()

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
