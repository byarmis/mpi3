#!/bin/python

import logging
from mpi3.view.menu_items import Button, MenuButton, SongButton

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


class Menu(object):
    def __init__(self, config, pop, items=None, home=False, filters=None):
        self.back = pop
        self.config = config

        if home:
            self.items = [MenuButton(button_type='MENU', text='Music'),
                          SongButton(song_id=1, play_song=lambda x: x, transfer_func=lambda x: x)]
        else:
            self.items = items or []
        self.home = home

        self.page_size = self.config['computed']['page_size']
        self.page = self.generate_page()
        self.filters = filters
        self.page_val = 0

    def __getitem__(self, item):
        return self.page[item]

    def generate_page(self):
        if self.home:
            p = [
                MenuButton(button_type='MENU', text='Music')
                , MenuButton(button_type='MENU', text='Settings')
                , MenuButton(button_type='MENU', text='About')
            ]

        else:
            p = [Button(text='  <', on_click=self.back)]

            # p.append(new button for each item returned by filter)
            # If the filter's an album, set that type
            # If the filter's an artist, set that type
            # If the filter's songs, those type

        return p


class MenuStack(Stack):
    def __init__(self, config):
        super(MenuStack, self).__init__()

        self.home_screen = Menu(pop=self.pop, config=config, home=True)
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
