#!/bin/python

import logging
from mpi3.view.menu_items import ViewItem, MenuButton, SongButton

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Stack(object):
    def __init__(self):
        self.stack = []

    def add(self, menu):
        self.stack.append(menu)

    def pop(self):
        return self.stack.pop()

    def peek(self):
        return self.stack[-1]

    def __nonzero__(self):
        return len(self.stack) > 0

    def __len__(self):
        return len(self.stack)


class Menu(ViewItem):
    def __init__(self, render_helper, items=None, home=False):
        super(Menu, self).__init__()

        self.config = render_helper.config
        self.render_helper = render_helper
        self.draw = self.render_helper.draw
        self.font = self.render_helper.font

        if home:
            self.items = [MenuButton(render_helper=self.render_helper
                                     , button_type='MENU'
                                     , text=' Music'),
                          SongButton(song_id=1, render_helper=render_helper,
                                     play_song=lambda x: x, transfer_func=lambda x: x)]
        else:
            self.items = items or []
        self.home = home

        self.page_size = self.config['computed']['page_size']
        self.paginated = self.generate_pages()
        self.page_val = 0

        self.page = self.paginated.next()

    def render(self):
        logger.debug('Rendering menu')
        offset = self.config['font']['title_size']
        for item in self.items:
            item.render(offset)
            offset += self.config['font']['size']

    def __repr__(self):
        return 'MENU'

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

class MenuStack(Stack):
    def __init__(self, render_helper):
        super(MenuStack, self).__init__()

        self.home_screen = Menu(render_helper=render_helper, home=True)
        self.add(self.home_screen)

        self._is_home = True

    def __repr__(self):
        return 'MENU STACK: {} items'.format(len(self.stack))

    def pop(self):
        if self._is_home:
            return
        else:
            p = self.stack.pop()
            self._is_home = self.peek() is self.home_screen
            return p

    def render(self):
        self.peek().render()
