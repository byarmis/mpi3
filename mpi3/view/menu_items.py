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


class Menu(ViewItem):
    def __init__(self, config, player, items, parent=None):
        super(Menu, self).__init__()

        self.items = items
        self.page_size = config['computed']['page_size']
        self.player = player
        self.paginated = self.generate_pages()
        self.page_val = 0
        self.parent = parent

        self._back_button = Button(config, draw, font, text, on_click)
        self.page = self.paginated.next()

    def render(self):
        logger.debug('Rendering menu')
        for item in self.items:
            item.render()

    def __repr__(self):
        return 'MENU'

    #     def previous(self):
    #         print('Going to previous')
    #         return self.parent
    #
    #     def get_child(self, val):
    #         # Get the item in the list selected by the cursor
    #         print(self.paginated[self.page_val][val])
    #
    def generate_pages(self):
        for i in range(0, len(self.items), self.page_size):
            yield self.items[i:i + self.page_size]


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

class Button(ViewItem):
    # A line item on the screen that can optionally be clicked
    def __init__(self, config, draw, font, text, on_click=None):
        super(Button, self).__init__()
        self.draw = draw
        self.font = font
        self.text = text
        self.BLACK = get_color(config, black=True)
        self._on_click = on_click

    def __repr__(self):
        return 'BUTTON: {}'.format(self.text)

    def __str__(self):
        return self.text

    def render(self, offset):
        self.draw.text((0, offset), ' ' + str(self), font=self.font, fill=self.BLACK)

    def on_click(self):
        if self._on_click is not None:
            self._on_click()


class SongButton(Button):
    def __init__(self, draw, font, text, font_color, song_id, play_song, transfer_func):
        super(SongButton, self).__init__()
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

    @property
    def y(self):
        return self.tfont_size + (self.font_size * self.value)

    def render(self):
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
