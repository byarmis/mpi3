#!/bin/python

import logging
from mpi3.model.menu_items import Button, MenuButton, SongButton, ViewItem
from mpi3.model.db import Database
from mpi3.model.constants import CURSOR_DIR

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

DATABASE = None


class Stack(object):
    def __init__(self, items=None):
        self.stack = items or []

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


class Cursor(ViewItem):
    def __init__(self):
        super(Cursor, self).__init__()

        self.value = 1

    def __repr__(self):
        return 'CURSOR'

    def __str__(self):
        return '>'

    def __add__(self, other):
        if not isinstance(other, int):
            raise ValueError, 'Can only add integers to cursor'
        self.value += other

    def __sub__(self, other):
        if not isinstance(other, int):
            raise ValueError, 'Can only subtract integers to cursor'
        self.value -= other

    def reset(self):
        self.value = 1


class IndividualMenu(object):
    def __init__(self, items=None, filters=None):
        global DATABASE

        self._db = DATABASE
        self.page = 0
        self.filters = filters or dict()
        self.buttons = items or []
        self.cursor = Cursor()

        if filters:
            if 'artist' in filters and 'album' not in filters:
                # TODO: Add
                # .extend
                self.buttons += []
            elif 'album' in filters:
                # TODO: Add
                self.buttons += []
            else:
                raise ValueError, 'Unknown item(s) in filters: {}'.format(
                    ', '.join(filters.keys()))

        self.strings = [str(i) for i in self.buttons]

    def _cursor_move(self, direction):
        v = self.cursor.value
        if 0 < v < len(self.buttons):
            self.cursor += direction
            return False  # Don't full redraw
        else:
            self.cursor.reset()
            self.page += direction
            return True

    def cursor_down(self):
        return self._cursor_move(CURSOR_DIR.DOWN)

    def cursor_up(self):
        return self._cursor_move(CURSOR_DIR.UP)

    def __iter__(self):
        return self._db.get_list(
            filters=self.filters,


        )


class Menu(object):
    # All menus
    def __init__(self, config, database):
        self.config = config
        self.is_home = True
        self.page_size = self.config['computed']['page_size']
        self.db = database

        self._menu_stack = Stack(self.generate_home())
        # TODO: Change for multiple menus
        # self.items = [IndividualMenu(items=(
        #     (MenuButton(menu_type='MENU', text='Music'),
        #      SongButton(song_id=1, play_song=lambda x: x, transfer_func=lambda x: x))
        # ))]

    @property
    def cursor_down(self):
        return self._menu_stack.peek().cursor_down

    @property
    def cursor_up(self):
        return self._menu_stack.peek().cursor_up

    def back(self):
        self._menu_stack.pop()

    @staticmethod
    def generate_home():
        return [
            MenuButton(menu_type='MENU', text='Music')
            , MenuButton(menu_type='MENU', text='Settings')
            , MenuButton(menu_type='MENU', text='About')
        ]

    def page(self):
        p = [Button(text='  <', on_click=self.back)]
        p.extend([Button(text=i.title, on_click=i.on_click) for i in self._menu_stack.peek()])

        # p.append(new button for each item returned by filter)
        # If the filter's an album, set that type
        # If the filter's an artist, set that type
        # If the filter's songs, those type

        return p

    def on_click(self):
        if self._menu_stack.peek().cursor.value > 0:
            # May change the screen or may have side-effects (change the current songlist / playlist)
            return self._menu_stack.peek().on_click()
        else:
            # They clicked the back button
            self._menu_stack.pop()

            # Always re-render
            return True

# class MenuStack(Stack):
#     def __init__(self, config):
#         super(MenuStack, self).__init__()
#
#         self.home_screen = Menu(config=config, home=True)
#         self.add(self.home_screen)
#
#         self._is_home = True
#
#     def __repr__(self):
#         return 'MENU STACK: {} items'.format(len(self.stack))
#
#     def pop(self):
#         if self._is_home:
#             return
#         else:
#             p = self.stack.pop()
#             self._is_home = self.peek() is self.home_screen
#             return p
