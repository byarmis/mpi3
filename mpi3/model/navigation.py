#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from mpi3.model.menu_items import Button, MenuButton, SongButton, ViewItem
from mpi3.model.db import Database
from mpi3.model.constants import CURSOR_DIR

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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

    def __eq__(self, other):
        return self.stack == other.stack


class Cursor(ViewItem):
    '''
    Range of (-inf, inf)
    '''

    # TODO: Should this have a lower limit of 0?
    def __init__(self):
        super(Cursor, self).__init__()
        self.value = 1

    def button_type(self):
        pass

    def __repr__(self):
        return 'CURSOR'

    def __str__(self):
        return '>'

    def __add__(self, other):
        if not isinstance(other, int):
            raise ValueError('Can only add integers to cursor')
        self.value += other

    def __sub__(self, other):
        if not isinstance(other, int):
            raise ValueError('Can only subtract integers from cursor')
        self.value -= other

    def reset(self):
        self.value = 1


class IndividualMenu(object):
    def __init__(self, page_size, items=None, filters=None):
        # TODO: Add ability to have items of multiple types, not just a big song list
        self.page = 0
        self.filters = filters or dict()
        self.buttons = items or []
        self.cursor = Cursor()
        self.page_size = page_size

        if filters:
            if 'artist' in filters and 'album' not in filters:
                # TODO: Add
                self.buttons += []
            elif 'album' in filters:
                # TODO: Add
                self.buttons += []
            else:
                raise ValueError('Unknown item(s) in filters: {}'.format(
                    ', '.join(filters.keys())))

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


class Menu(object):
    # All menus
    def __init__(self, config, db):
        self.config = config
        self.is_home = True
        self.page_size = self.config['computed']['page_size']
        self._menu_stack = Stack([self.generate_home()])
        self.db = db

    def __iter__(self):
        return iter(self.db.get_list(
            filters=self._menu_stack.peek().filters,
            limit=self.page_size,
            offset=self.page_size * self.page
        ))

    @property
    def cursor_down(self):
        return self._menu_stack.peek().cursor_down

    @property
    def cursor_up(self):
        return self._menu_stack.peek().cursor_up

    def back(self):
        self._menu_stack.pop()

    def generate_home(self):
        return IndividualMenu(page_size=self.config['computed']['page_size'],
                              items=[MenuButton(menu_type='MENU', text='Music')
                                  , MenuButton(menu_type='MENU', text='Settings')
                                  , MenuButton(menu_type='MENU', text='About')
                                     ])

    def page(self):
        p = [Button(text='  <', on_click=self.back)]
        p.extend([Button(text=i.title, on_click=i.on_click) for i in self._menu_stack.peek()])

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


class Title(ViewItem):
    def __init__(self, state, vol):
        self.state = state
        self.vol = vol

    def __str__(self):
        return '{state}  {vol}'.format(state=self.state,
                                       vol=self.vol)

    def __repr__(self):
        return 'TITLE'

    def button_type(self):
        pass

    # @property
    # def time(self):
    #     return dt.now().strftime('%I:%M')
