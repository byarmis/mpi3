#!/bin/python
import yaml
import os
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
    logger.debug('Parsed the following config file:\n{}'.format(c))
    return c


def scan_libraries(locs):
    logger.debug('Scanning following directory(s):{}'.format('\n\t'.join(locs)))
    files = []

    for loc_raw in locs:
        loc = os.path.expanduser(loc_raw)
        logger.debug('Scanning {raw}, expanded to {expanded}'.format(raw=loc_raw, expanded=loc))

        for (dirpath, _, filename) in os.walk(loc):
            if filename:
                files.extend(os.path.join(dirpath, f) for f in filename)

    if not files:
        logger.warn('No files found')

    logger.info('Total of {} files found in {} music directory(s)'.format(len(files), len(locs)))
    return files


def setup_buttons(config, **kwargs):
    GPIO.setmode(GPIO.BCM)

    for name, val in config['buttons'].iteritems():
        logger.debug('Setting pin {} to be {}'.format(val, name))
        GPIO.setup(val, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    for k, v in kwargs.iteritems():
        GPIO.add_event_detect(config['buttons'][k], GPIO.FALLING, v)
