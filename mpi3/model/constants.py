from collections import namedtuple

_state_list = ['NORMAL', 'SHUFFLE', 'LOOP', 'REPEAT']
_states = namedtuple('PLAYBACK_STATES', _state_list)
PLAYBACK_STATES = _states(*_state_list)

_dir_list = ['FORWARD', 'BACKWARD']
_directions = namedtuple('DIRECTION', _dir_list)
DIRECTION = _directions(*_dir_list)

_mode_list = ['NORMAL', 'VOLUME', 'PLAYBACK']
_modes = namedtuple('BUTTON_MODE', _mode_list)
BUTTON_MODE = _modes(*_mode_list)
