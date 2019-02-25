#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from datetime import datetime as dt
from cachetools import cached, TTLCache

from mpi3.model.menu_items import Button, MenuButton, SongButton, ShellButton
from mpi3.model.constants import CURSOR_DIR

logger = logging.getLogger(__name__)


class Stack:
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


class SongMenu:
    # What's on screen at the moment

    def __init__(self, page_size, song_list):
        # TODO: Add ability to have items of multiple types, not just a big song list
        self.page = 0
        self.song_list = song_list
        self.page_size = page_size
        self.INITIAL_CURSOR_VAL = 0
        self.cursor_val = self.INITIAL_CURSOR_VAL  # TODO: Change to 1 when multimenus are a thing

    def _cursor_move(self, direction):
        self.song_list.song_counter += direction

        if 0 <= self.cursor_val + direction < len(self.song_list):
            logger.debug('Moving the cursor within a page')
            self.cursor_val += direction

            # Don't full redraw
            return True
        else:
            logger.debug('Moving the cursor and changing pages')

            # Change pages and reset the cursor location to the first item
            self.cursor_val = self.INITIAL_CURSOR_VAL
            self.page += direction
            if self.page < 0:
                # If we went backwards, go to the previous page
                self.page = (len(self.song_list) // self.page_size) + 1

            self.song_list.page = self.page
            self.song_list.refresh_list()

            self.strings = [str(i) for i in self.song_list]
            # Full redraw
            return False

    def cursor_down(self):
        return self._cursor_move(CURSOR_DIR.DOWN)

    def cursor_up(self):
        return self._cursor_move(CURSOR_DIR.UP)

    def items(self):
        return [str(i) for i in self.song_list]

    def on_click(self):
        return self.song_list[self.cursor_val].on_click()


class SettingsMenu:
    def __init__(self, directory, items, cursor_val=1):
        logger.debug('Generating Settings Menu')

        self.cursor_val = cursor_val
        self.buttons = []
        for item in items:
            self.buttons.append(ShellButton(text=list(item.keys())[0],
                                            directory=directory,
                                            shell_script=list(item.values())[0]))

    def on_click(self):
        _ = self.buttons[self.cursor_val].on_click()
        return False

    def cursor_down(self):
        if self.cursor_val == len(self.buttons) - 1:
            self.cursor_val = 0
        else:
            self.cursor_val += 1
        return True

    def cursor_up(self):
        if self.cursor_val == 0:
            self.cursor_val = len(self.buttons) - 1
        else:
            self.cursor_val -= 1
        return True

    def items(self):
        return (str(b) for b in self.buttons)


class Menu:
    # All menus
    def __init__(self, config, db, song_list):
        self.config = config
        self.is_home = True
        self.page_size = self.config['computed']['page_size']
        self.db = db
        self.song_list = song_list
        self._layout = self.config['menu']['layout']['home']
        self._menu_stack = Stack([self.generate_home()])

    @property
    def items(self):
        return self._menu_stack.peek().items()

    def cursor_down(self):
        return self._menu_stack.peek().cursor_down()

    def cursor_up(self):
        return self._menu_stack.peek().cursor_up()

    def back(self):
        self._menu_stack.pop()
        return True

    def generate_home(self):
        # return SettingsMenu(directory=self.config['menu']['shell_scripts'],
        #                     items=self._layout[-1]['settings']['items'],
        #                     cursor_val=0)
        return SongMenu(page_size=self.page_size,
                        song_list=self.song_list)

        # from mpi3.model.model import SongList
        # f = lambda x: None
        #
        # return SongMenu(page_size=self.page_size,
        #                 song_list=SongList(db=self.db,
        #                                    page_size=self.page_size,
        #                                    play_song=f))
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
        if self._menu_stack.peek().cursor_val > 0 or len(self._menu_stack) == 1:
            # May change the screen or may have side-effects (change the current songlist / playlist)
            self._menu_stack.peek().on_click()
        else:
            logger.debug('Going back a menu')
            # They clicked the back button
            self._menu_stack.pop()

        # Always re-render
        return True


class Title:
    def __init__(self, state, vol):
        self.state = state
        self.vol = vol

    def __str__(self):
        return '{state}   {time}  {vol}'.format(state=self.state,
                                                vol=self.vol,
                                                time=self.time)

    def __repr__(self):
        return 'TITLE'

    @property
    @cached(cache=TTLCache(maxsize=1, ttl=10))
    def time(self):
        # No idea how reliable this is
        logger.warning('Getting the time ({})-- is this reliable?'.format(dt.now().strftime('%I:%M')))
        return dt.now().strftime('%I:%M')
