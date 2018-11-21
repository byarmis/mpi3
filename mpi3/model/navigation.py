#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from datetime import datetime as dt

from mpi3.model.menu_items import Button, MenuButton, SongButton, ViewItem
from mpi3.model.constants import CURSOR_DIR

logger = logging.getLogger(__name__)

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


class SongMenu(object):
    # What's on screen at the moment

    def __init__(self, page_size, song_list):
        # TODO: Add ability to have items of multiple types, not just a big song list
        self.page = 0
        self.song_list = song_list
        self.page_size = page_size
        self.cursor_val = 1

        self.strings = [str(i) for i in self.song_list]

    def _cursor_move(self, direction):
        self.song_list.song_counter += direction

        if 0 < self.cursor_val < len(self.song_list):
            self.cursor_val += direction

            # Don't full redraw
            return False
        else:
            # Change pages and reset the cursor location to the first item
            self.cursor_val = 1
            self.page += direction
            if self.page < 0:
                # If we went backwards, go to the previous page
                self.page = (len(self.song_list) // self.page_size) + 1
            self.song_list.refresh_list()

            self.strings = [str(i) for i in self.song_list]
            # Full redraw
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

    def cursor_down(self):
        return self._menu_stack.peek().cursor_down()

    def cursor_up(self):
        return self._menu_stack.peek().cursor_up()

    def back(self):
        self._menu_stack.pop()
        return True

    def generate_home(self):
        from mpi3.model.model import SongList
        return SongMenu(page_size=self.page_size,
                        song_list=SongList(db=self.db, page_size=self.page_size))
        # return IndividualMenu(page_size=self.config['computed']['page_size'],
        #                       items=[MenuButton(menu_type='MENU', text='Music'),
        #                              MenuButton(menu_type='MENU', text='Settings'),
        #                              MenuButton(menu_type='MENU', text='About')])

        # def page(self):
        #     p = [Button(text='  <', on_click=self.back)]
        #     p.extend([Button(text=i.title, on_click=i.on_click) for i in self._menu_stack.peek()])
        #
        #     return p

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

    @property
    def time(self):
        # No idea how reliable this is
        logger.warning('Getting the time ({})-- is this reliable?'.format(dt.now().strftime('%I:%M')))
        return dt.now().strftime('%I:%M')
