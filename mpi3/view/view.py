#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
from PIL import Image, ImageDraw, ImageFont

from papirus import Papirus

logger = logging.getLogger(__name__)


class Renderer(object):
    def __init__(self, screen_size, image, font, tfont, papirus, white, black):
        self._image = image
        self._draw = ImageDraw.Draw(self._image)

        self.size = screen_size
        self.papirus = papirus

        self.WHITE = white
        self.BLACK = black

        self.font = font
        self.tfont = tfont

        self.partial_update = False

    def render_title(self, title):
        logger.debug('Rendering title: {} ({})'.format(title, type(title)))
        self._draw.text((0, 0), str(title), font=self.tfont, fill=self.BLACK)

    def render_cursor(self, i):
        logger.debug('Rendering cursor')
        self._draw.text((0, (i * self.font.size) + self.tfont.size), '>',
                        font=self.font, fill=self.BLACK)

    def render(self, title, items, cursor_val, partial=False):
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
        self.update(partial=partial)

    def blank(self):
        logger.debug('Blanking')
        self._draw.rectangle((0, 0) + self.size, fill=self.WHITE, outline=self.WHITE)

    def update(self, partial):
        logger.debug('Updating ({})'.format('partially' if self.partial_update else 'completely'))
        if self.partial_update or partial:
            self.papirus.partial_update()
        else:
            self.papirus.update()
            self.partial_update = True


class View(object):
    def __init__(self, config):
        self.config = config

        self.papirus = Papirus(rotation=90)
        self.papirus.clear()

        self.screen_size = (config['screen_size']['width']
                            , config['screen_size']['height'])

        font_file = self.config['font']['file']

        logger.debug('Font file: {}, expanded to {}'.format(
                font_file, os.path.expanduser(font_file)
        ))

        def get_font(s):
            return ImageFont.truetype(os.path.expanduser(font_file), s)

        render_options = {
            'font': get_font(self.config['font']['size']),
            'tfont': get_font(self.config['font']['title_size']),
            'white': config['colors']['white'],
            'black': config['colors']['black'],
            'papirus': self.papirus,
            'image': Image.new('1', self.screen_size, config['colors']['white']),
            'screen_size': self.screen_size,
        }

        self.renderer = Renderer(**render_options)

    def render(self, *args, **kwargs):
        self.renderer.render(*args, **kwargs)
