#!/bin/python
import yaml
import logging

import RPi.GPIO as GPIO

logger = logging.getLogger(__name__)


def get_config():
    logger.debug('Getting config')
    with open('./config.yaml') as f:
        logger.debug('Loading yaml file')
        c = yaml.load(f)
        logger.debug('yaml file loaded')

    c['computed'] = {}
    c['computed']['page_size'] = (c['screen_size']['height'] - c['font']['title_size']) // c['font']['size']

    return c


def setup_buttons(config, **kwargs):
    GPIO.setmode(GPIO.BCM)

    for name, val in config['buttons'].items():
        logger.debug('Setting pin {} to be {}'.format(val, name))
        GPIO.setup(val, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    for k, v in kwargs.iteritems():
        GPIO.add_event_detect(config['buttons'][k], GPIO.FALLING, v)
