from collections import namedtuple

_dir_list = ['FORWARD', 'BACKWARD']
_directions = namedtuple('DIRECTION', _dir_list)
DIRECTION = _directions(*_dir_list)

_mode_list = ['NORMAL', 'VOLUME', 'PLAYBACK']
_modes = namedtuple('BUTTON_MODE', _mode_list)
BUTTON_MODE = _modes(*_mode_list)

_cursor_dir = namedtuple('DIRECTION', ['DOWN', 'UP'])
CURSOR_DIR = _cursor_dir(DOWN=1, UP=-1)

