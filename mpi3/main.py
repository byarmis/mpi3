#!/bin/python
from controller.player import Player
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    logger.debug('Initializing player')
    p = Player()
    logger.debug('Running player')
    p.run()
    logger.debug('Running player-- COMPLETE')
