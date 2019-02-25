#!/usr/bin/env python3
from collections import namedtuple

_dir_list = ['FORWARD', 'BACKWARD']
_directions = namedtuple('DIRECTION', _dir_list)
DIRECTION = _directions(*_dir_list)

_mode_list = ['NORMAL', 'VOLUME', 'PLAYBACK']
_modes = namedtuple('BUTTON_MODE', _mode_list)
BUTTON_MODE = _modes(*_mode_list)

_cursor_dir = namedtuple('DIRECTION', ['DOWN', 'UP'])
CURSOR_DIR = _cursor_dir(DOWN=1, UP=-1)

_playback_states = namedtuple('PLAYBACK', ['PLAY', 'PAUSE', 'DONE'])
PLAYBACK_STATES = _playback_states(PLAY=1, PAUSE=2, DONE=0)

mpg_123_STATES = {
    b'@P 0': PLAYBACK_STATES.DONE,
    b'@P 1': PLAYBACK_STATES.PAUSE,
    b'@P 2': PLAYBACK_STATES.PLAY,
}
