import os
from draw_tools import *

_WELCOME_TEXT = 'NPMGR 0.1'
_PADDING = 2

def _col():
    return os.get_terminal_size()[0]


def _ln():
    return os.get_terminal_size()[1]


def draw_welcome_box():
    total_width = len(_WELCOME_TEXT) + _PADDING * 2

    ln1 = bgstr(' '*total_width)
    ln2 = bgstr(' '*_PADDING + _WELCOME_TEXT + ' '*_PADDING)
    
    scol = int(_col() / 2 - total_width / 2)
    midy = int(_ln() / 2)

    tprint(scol, midy - 1, ln1)
    tprint(scol, midy, ln2)
    tprint(scol, midy + 1, ln1)


if __name__ == '__main__':
    draw_welcome_box()
