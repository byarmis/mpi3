#!/bin/python3
import argparse
import logging
from datetime import datetime
from controller.player import Player

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A Raspberry Pi-based MP3 player',
                                     epilog='For bugs, questions, and discussion, see https://gitlab.com/byarmis/mpi3',
                                     prog='mpi3')

    parser.add_argument('--config-file', '-c', type=str, default='./config.yaml',
                        help='file path for the config file to use')

    parser.add_argument('--verbose', '-v', action='count', default=None,
                        help='''
                        verbosity level for logging.
                        \n\t-v   for INFO
                        \n\t-vv  for DEBUG
                        Default is WARNING''')

    parser.add_argument('--quiet', '-q', action='count', default=None,
                        help='''
                        makes logging quieter than default.
                        \n\t-q   for ERROR
                        \n\t-qq  for CRITICAL.  
                        Default is WARNING''')

    parser.add_argument('--log-file', '-l', type=str, default=datetime.now().strftime('%Y%m%d%H%M%s_mpi3.log'),
                        help='the file to log to, if any.  If "False" (case-insensitive), will log to stdout instead')

    logger.debug('Initializing player')
    p = Player(args=parser.parse_args())
    logger.debug('Running player')
    p.run()
    logger.debug('Running player-- COMPLETE')
