#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import logging
from datetime import datetime

from mpi3.controller.player import Player

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A Raspberry Pi-based MP3 player',
                                     epilog='For bugs, questions, and discussion, see https://gitlab.com/byarmis/mpi3',
                                     prog='mpi3')

    # TODO: Might need to change                                     \/
    parser.add_argument('--config-file', '-c',
                        dest='config_file',
                        type=str,
                        default='./mpi3/config.yaml',
                        help='File path for the config file to use')

    parser.add_argument('--log', '-l',
                        dest='log_level',
                        type=str,
                        default='WARNING',
                        help='''Verbosity level for logging.  Options are case-insensitive and:
                                \n\tDEBUG
                                \n\tINFO
                                \n\tWARNING
                                \n\tERROR
                                \n\tCRITICAL
                                Default is WARNING''')

    parser.add_argument('--log-file', '-l',
                        dest='log_file',
                        type=str,
                        default=datetime.now().strftime('%Y%m%d%H%M%s_mpi3.log'),
                        help='''The file to log to, if any.
                                If "False" (case-insensitive), will log to stdout instead.''')

    args = parser.parse_args()

    log_level = getattr(logging, args.log_level.upper(), None)
    assert log_level is not None, 'Invalid log level: {}'.format(log_level)

    if args.log_file.lower().strip() == 'false':
        import sys
        logging.basicConfig(level=log_level, stream=sys.stdout)
    else:
        logging.basicConfig(level=log_level, filename=args.log_file)

    logger.info('Initializing player')
    p = Player(args=args)
    logger.info('Running player')
    p.run()
    logger.critical('Running player-- COMPLETE')

