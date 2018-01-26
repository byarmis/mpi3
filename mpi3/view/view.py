#!/bin/python
import os
import logging
from PIL import Image, ImageDraw, ImageFont

from papirus import Papirus
from mpi3.model.constants import CURSOR_DIR
from utils import get_screen_size, get_color, RenderHelper
from menu_items import Title, Cursor
from mpi3.model.navigation import MenuStack

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
    def __init__(self, screen_size, image, draw, font, tfont, papirus, title, cursor, menu, white, black):
        self._image = image
        self._draw = ImageDraw.Draw(self._image)

        self.size = screen_size
        self.draw = draw
        self.papirus = papirus

        self.WHITE = white
        self.BLACK = black

        self.font = font
        self.tfont = tfont

        self.title = title
        self.cursor = cursor
        self.menu = menu

        self.partial_update = False

    def render_title(self):
        logger.debug('Rendering title')
        self._draw.text((0, 0), self.title, font=self.tfont, fill=self.BLACK)

    def render_cursor(self):
        logger.debug('Rendering cursor')
        self._draw.text((0, self.cursor.value * self.font + self.tfont), self.cursor, font=self.font, fill=self.BLACK)

    def render(self, partial=None):
        self.blank()
        logger.debug('Rendering')
        self.render_title()
        self.render_cursor()

        offset = self.tfont.size

        for item in self.menu:
            logger.debug('\t{}'.format(repr(i)))
            self._draw.text((0, offset), item, font=self.font, fill=self.BLACK)

            offset += self.font.size

        self.papirus.display(self._image)
        self.update(partial=partial)

    def blank(self):
        logger.debug('Blanking')
        self._draw.rectangle((0, 0) + self.size, fill=self.WHITE, outline=self.WHITE)

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
        self._play_song = play_song
        self._transfer_func = transfer_func

        self.papirus = Papirus(rotation=90)
        self.papirus.clear()

        self.screen_size = get_screen_size(config)

        font_dir = self.config['font']
        font_size = self.config['font']['size']
        tfont_size = self.config['font']['title_size']
        get_font = lambda font_dir, size: ImageFont.truetype(os.path.expanduser(font_dir), size)

        render_options = {
            'font': get_font(font_dir, font_size),
            'tfont': get_font(font_dir, tfont_size),
            'white': config['colors']['white'],
            'black': config['colors']['black'],
            'papirus': self.papirus,
            'image': Image.new('1', self.screen_size, config['colors']['white']),
            'screen_size': self.screen_size
        }

        self._title = Title(state=playback_state, vol=volume)
        self._cursor = Cursor()
        self._menu = MenuStack(config)

        self.renderer = Renderer(title=self._title
                                 , cursor=self._cursor
                                 , menu=self._menu
                                 , **render_options
                                 )

    def move_cursor(self, direction=None, reset=False):
        # TODO: Flesh out with menu/screen changing (w/ cursor resetting) and all that fun stuff

        # Move the cursor in the direction

        # Did it go outside bounds?

        # If it did, reset it

        # Go to the next menu page (+/- 1)

        # If the menu went to the next page, rerender fully

        # If the menu didn't (small number of items), partial update
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
