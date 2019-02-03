#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml
import logging
import os

import RPi.GPIO as GPIO

logger = logging.getLogger(__name__)


def get_config(config):
    config_path = os.path.expanduser(config)
    logger.debug('Getting config {}'.format(config_path))
    with open(config_path) as f:
        logger.debug('Loading yaml file')
        c = yaml.load(f)
        logger.debug('yaml file loaded')

    c['computed'] = {}

    menu_path = os.path.expanduser(c['menu']['file'])
    with open(menu_path) as f:
        logger.debug('Loading menu config')
        c['menu']['layout'] = yaml.load(f)
        logger.debug('yaml file loaded')

    c['computed']['page_size'] = (c['screen_size']['height'] - c['font']['title_size']) // c['font']['size']

    return c


def setup_buttons(config, **kwargs):
    GPIO.setmode(GPIO.BCM)

    for name, val in config['buttons'].items():
        logger.debug('Setting pin {} to be {}'.format(val, name))
        GPIO.setup(val, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    for k, v in kwargs.items():
        GPIO.add_event_detect(config['buttons'][k], GPIO.FALLING, v)
