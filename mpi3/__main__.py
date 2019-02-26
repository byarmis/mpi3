#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import os

from mpi3.controller.player import MPi3Player

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A Raspberry Pi-based MP3 player',
                                     epilog='For bugs, questions, and discussion, see https://gitlab.com/byarmis/mpi3',
                                     prog='mpi3')

    parser.add_argument('--config-file', '-c',
                        dest='config_file',
                        type=str,
                        # TODO: Might need to change below
                        default='./mpi3/config.yaml',
                        help='File path for the config file to use')

    parser.add_argument('--log-level', '-ll',
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

    parser.add_argument('--log-file', '-lf',
                        dest='log_file',
                        type=str,
                        default='~/mpi3/logs/mpi3.log',
                        help='''The file to log to, if any.  
                                If "False" (case-insensitive), will log to stdout instead.  
                                Defaults to ~/mpi3/logs/mpi3.log''')

    parser.add_argument('--log-file-count', '-lfc',
                        dest='log_file_count',
                        type=int,
                        default=5,
                        help='''The number of log file backups to keep
                                Defaults to 5''')

    parser.add_argument('--log-file-size', '-lfs',
                        dest='log_file_size',
                        type=int,
                        default=500,
                        help='''The maximum size, in megabytes, that the log file should
                                grow to.
                                Defaults to 500''')

    args = parser.parse_args()

    log_level = getattr(logging, args.log_level.upper(), None)
    assert log_level is not None, 'Invalid log level: {}'.format(log_level)

    if args.log_file.lower().strip() == 'false':
        import sys

        logging.basicConfig(level=log_level, stream=sys.stdout)

    else:
        import logging.handlers

        log_file = os.path.expanduser(args.log_file)
        if not os.path.exists(os.path.dirname(log_file)):
            os.makedirs(os.path.dirname(log_file))

        logging.basicConfig(level=log_level, filename=log_file)
        handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=1024 * args.log_file_size,
                backupCount=args.log_file_count)

        logger.addHandler(handler)

    # noinspection PyBroadException
    try:
        logger.info('Initializing player')
        p = MPi3Player(args=args)
        logger.info('Running player')
        p.run()
        logger.critical('Running player-- COMPLETE')

    except BaseException as e:
        if str(e):
            # noinspection PyPep8Naming
            from papirus import PapirusText as PT

            logger.warning('Exception raised:')
            logger.warning(repr(e))

            PT().write(repr(e), size=13)

        else:
            # noinspection PyPep8Naming
            from papirus import PapirusImage as PI

            dir_path = os.path.dirname(os.path.realpath(__file__))
            PI(rotation=90).write(os.path.join(dir_path, 'static', 'imgs', 'exclamation.bmp'))
