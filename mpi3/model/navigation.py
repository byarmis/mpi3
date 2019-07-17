#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from datetime import datetime as dt
import logging
from typing import Tuple, Iterable, Any

from mpi3.model.menu_items import Button, MenuButton, SongButton, ShellButton
from mpi3.model.constants import CURSOR_DIR
from mpi3.view.view import HowUpdate

logger = logging.getLogger(__name__)


class Stack:
    def __init__(self, items: Iterable = None) -> None:
        self.stack = items or []

    def add(self, menu: Any) -> None:
        self.stack.append(menu)

    def pop(self) -> Any:
        return self.stack.pop()

    def peek(self) -> Any:
        return self.stack[-1]

    def __nonzero__(self) -> bool:
        return len(self.stack) > 0

    def __len__(self) -> int:
        return len(self.stack)

    def __eq__(self, other: 'Stack') -> bool:
        return self.stack == other.stack


class BaseMenu(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def on_click(self):
        pass

    @abstractmethod
    def cursor_down(self):
        pass

    @abstractmethod
    def cursor_up(self):
        pass

    @property
    @abstractmethod
    def items(self):
        pass


class SongMenu(BaseMenu):
    # What's on screen at the moment

    def __init__(self, page_size, song_list):
        self.page = 0
        self.page_size = page_size
        self.song_list = song_list
        self.INITIAL_CURSOR_VAL = 0
        self.cursor_val = self.INITIAL_CURSOR_VAL  # TODO: Change to 1 when multimenus are a thing

    def _cursor_move(self, direction) -> HowUpdate:
        self.song_list.song_counter += direction

        if 0 <= self.cursor_val + direction < len(self.song_list):
            logger.debug('Moving the cursor within a page')
            self.cursor_val += direction

            # Don't full redraw
            return HowUpdate(partial=True)
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
            return HowUpdate(complete=True)

    def cursor_down(self) -> HowUpdate:
        return self._cursor_move(CURSOR_DIR.DOWN)

    def cursor_up(self) -> HowUpdate:
        return self._cursor_move(CURSOR_DIR.UP)

    def items(self) -> Tuple[str]:
        return tuple(str(i) for i in self.song_list)

    def on_click(self) -> HowUpdate:
        return self.song_list[self.cursor_val].on_click()


class SettingsMenu(BaseMenu):
    def __init__(self, config, items, cursor_val=1):
        logger.debug('Generating Settings Menu')

        self.page_counter = 0
        self.cursor_val = cursor_val
        self.pages = []
        page = []
        for item in items:
            script, quit = list(items.values())

            page.append(ShellButton(text=list(item.keys())[0],
                                    directory=config['menu']['shell_scripts'],
                                    shell_script=script,
                                    quit=quit,
                                    env_vars=config['env_vars']))

            if len(page) == config['computed']['page_size']:
                self.pages.append(page)
                page = []

    def on_click(self) -> HowUpdate:
        _ = self.page[self.cursor_val].on_click()
        return HowUpdate(complete=True)

    def cursor_down(self) -> HowUpdate:
        if self.cursor_val == len(self.page) - 1:
            self.cursor_val = 0

            self.page_counter += 1
            self.page_counter %= len(self.pages)

            # Full redraw
            return HowUpdate(complete=True)

        else:
            self.cursor_val += 1
            return HowUpdate(partial=True)

    def cursor_up(self) -> HowUpdate:
        if self.cursor_val == 0:
            self.page_counter = len(self.pages) - 1
            self.cursor_val = len(self.page) - 1

        else:
            self.cursor_val -= 1
        return HowUpdate(partial=True)

    def items(self) -> Tuple[str]:
        return tuple(str(b) for b in self.page)

    @property
    def page(self):
        return self.pages[self.page_counter]


class MenuMenu(BaseMenu):
    """
    Weird name, I know.  It's for menus that contain just other menus
    """

    def __init__(self):
        pass

    def on_click(self):
        pass

    def cursor_down(self):
        pass

    def cursor_up(self):
        pass

    def items(self):
        pass


class Menu:
    # All menus
    def __init__(self, config, db, song_list):
        self.config = config
        self.is_home = True
        self.page_size = self.config['computed']['page_size']
        self.db = db
        self.song_list = song_list
        self._layout = self.config['menu']['layout']['home']
        self.menu_stack = Stack([self.generate_home()])

    @property
    def items(self):
        return self.menu_stack.peek().items()

    def cursor_down(self):
        return self.menu_stack.peek().cursor_down()

    def cursor_up(self):
        return self.menu_stack.peek().cursor_up()

    def back(self):
        _ = self.menu_stack.pop()
        return True

    def generate_home(self):
        return SettingsMenu(config=self.config,
                            items=self._layout[-1]['settings']['items'],
                            cursor_val=0)

        # return SongMenu(page_size=self.page_size,
        #                 song_list=self.song_list)

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

    def on_click(self) -> HowUpdate:
        if self.menu_stack.peek().cursor_val > 0 or len(self.menu_stack) == 1:
            # May change the screen or may have side-effects (change the current songlist / playlist)
            oc = self.menu_stack.peek().on_click()
            if isinstance(oc, BaseMenu):
                # Clicking on the button returned a new menu
                # Catch it and put it on the stack
                self.menu_stack.add(oc)
                return HowUpdate(complete=True)

            else:
                return oc
        else:
            logger.debug('Going back a menu')
            # They clicked the back button
            self.menu_stack.pop()

            # Always full re-render
            return HowUpdate(complete=True)


class Title:
    def __init__(self, state, vol) -> None:
        self.state = state
        self.vol = vol

    def __str__(self) -> str:
        return f'{self.state}   {self.time}  {self.vol}'

    def __repr__(self) -> str:
        return f'TITLE(state={self.state}, vol={self.vol})'

    @property
    def time(self) -> str:
        # No idea how reliable this is
        return dt.now().strftime('%I:%M')
