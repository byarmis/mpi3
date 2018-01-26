#!/bin/python
from PIL import Image, ImageDraw
import logging

from papirus import Papirus
from mpi3.model.constants import CURSOR_DIR
from utils import get_screen_size, get_color, get_font, RenderHelper
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
    def __init__(self, render_helper, image, targets, papirus):
        self.image = image
        self.size = get_screen_size(render_helper.config)
        self.draw = render_helper.draw
        self.WHITE = get_color(config=render_helper.config, white=True)
        self.targets = targets
        self.papirus = papirus

        self.partial_update = False
        self._render_helper = render_helper

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
        self._render_helper.draw.rectangle((0, 0) + self.size, fill=self.WHITE, outline=self.WHITE)

    def update(self, partial):
        logger.debug('Updating ({})'.format('partially' if self.partial_update else 'completely'))
        if self.partial_update or partial:
            self.papirus.partial_update()
        else:
            self.papirus.update()
            self.partial_update = True


class View(object):
    def __init__(self, playback_state, volume, config, play_song, transfer_func):
        self.screen_size = get_screen_size(config)

        self.WHITE = get_color(config, white=True)
        self.BLACK = get_color(config, black=True)

        self.papirus = Papirus(rotation=90)
        self.papirus.clear()

        self.image = Image.new('1', self.screen_size, self.WHITE)
        self._play_song = play_song
        self._transfer_func = transfer_func

        font = get_font(config, 'size')
        title_font = get_font(config, 'title_size')
        draw = ImageDraw.Draw(self.image)
        self._render_helper = RenderHelper(config=config, draw=draw, font=font, tfont=title_font)

        self._title = Title(render_helper=self._render_helper, state=playback_state, vol=volume)
        self._cursor = Cursor(self._render_helper)
        self._menu = MenuStack(self._render_helper)

        self.renderer = Renderer(render_helper=self._render_helper
                                 , image=self.image
                                 , papirus=self.papirus
                                 , targets=(self._cursor, self._title, self._menu)
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
