#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import toml
import logging
import os

import RPi.GPIO as GPIO

logger = logging.getLogger(__name__)


def get_config(config: str) -> dict:
    config_path = os.path.expanduser(config)
    logger.debug(f'Getting config {config_path}')
    with open(config_path) as f:
        c = toml.load(f)

    c['computed'] = {}

    logger.debug('Loading menu config')
    menu_path = os.path.expanduser(c['menu']['file'])
    with open(menu_path) as f:
        c['menu']['layout'] = toml.load(f)

    c['computed']['page_size'] = (c['screen']['height'] - c['font']['title_size']) // c['font']['size']

    return c


def setup_buttons(config: dict, **kwargs) -> None:
    GPIO.setmode(GPIO.BCM)

    for name, val in config['buttons'].items():
        logger.debug(f'Setting pin {val} to be {name}')
        GPIO.setup(val, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    for k, v in kwargs.items():
        GPIO.add_event_detect(config['buttons'][k], GPIO.FALLING, v)

