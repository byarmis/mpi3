#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
from contextlib import contextmanager
from PIL import Image, ImageDraw, ImageFont

from papirus import Papirus

from mpi3.view.types import HowUpdate

logger = logging.getLogger(__name__)


class Renderer:
    def __init__(self, screen_size, image, font, tfont, papirus, white, black) -> None:
        self._image = image
        self._draw = ImageDraw.Draw(self._image)

        self.size = screen_size
        self.papirus = papirus

        self.WHITE = white
        self.BLACK = black

        self.font = font
        self.tfont = tfont
        self.rendering = False

    @contextmanager
    def render_lock(self) -> None:
        self.rendering = True
        yield
        self.rendering = False

    def render_title(self, title) -> None:
        logger.debug('Rendering title: {}'.format(title))
        self._draw.text((0, 0), str(title),
                        font=self.tfont, fill=self.BLACK)

    def render_cursor(self, i: int) -> None:
        logger.debug('Rendering cursor')
        self._draw.text((0, (i * self.font.size) + self.tfont.size), '>',
                        font=self.font, fill=self.BLACK)

    def render(self, title, items, cursor_val, how_update: HowUpdate) -> None:
        if self.rendering:
            return

        with self.render_lock():
            self.blank()
            logger.debug('Rendering')
            self.render_title(title)
            self.render_cursor(cursor_val)

            offset = self.tfont.size

            for item in items:
                logger.debug('\t{}'.format(repr(item)))
                self._draw.text((0, offset), ' ' + item,
                                font=self.font, fill=self.BLACK)

                offset += self.font.size

            self.papirus.display(self._image)
            self.update(how_update)

    def blank(self) -> None:
        logger.debug('Blanking')
        self._draw.rectangle((0, 0) + self.size, fill=self.WHITE, outline=self.WHITE)

    def update(self, how_update: HowUpdate) -> None:
        if how_update.partial:
            logger.debug('Updating (partially)')
            self.papirus.partial_update()
        else:
            logger.debug('Updating (completely)')
            self.papirus.update()


class View:
    def __init__(self, config: dict) -> None:
        self.config = config

        self.papirus = Papirus(rotation=90)
        self.papirus.clear()

        self.screen_size = (config['screen_size']['width']
                            , config['screen_size']['height'])

        self._font_file = os.path.expanduser(self.config['font']['file'])

        render_options = {
            'font': self.get_font(self.config['font']['size']),
            'tfont': self.get_font(self.config['font']['title_size']),
            'white': config['colors']['white'],
            'black': config['colors']['black'],
            'papirus': self.papirus,
            'image': Image.new('1', self.screen_size, config['colors']['white']),
            'screen_size': self.screen_size,
        }

        self.renderer = Renderer(**render_options)

    def get_font(self, s: int) -> None:
        return ImageFont.truetype(os.path.expanduser(self._font_file), s)

    def render(self, *args, **kwargs) -> None:
        self.renderer.render(*args, **kwargs)
