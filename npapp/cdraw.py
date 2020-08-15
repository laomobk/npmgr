import termios
import sys
import readline
import os
from typing import List

_STDIN_FD = sys.stdin.fileno()
_TCATTR_OLD = termios.tcgetattr(_STDIN_FD)[:]

TCATTR_COMMON = _TCATTR_OLD[:]

TCATTR_NOECHO = TCATTR_COMMON[:]
TCATTR_NOECHO[3] &= ~termios.ECHO

TCATTR_IMMEDIATE = TCATTR_NOECHO[:]
TCATTR_IMMEDIATE[3] &= ~termios.ICANON


class TcAttrContext:
    def __init__(self, tcattr :List[int]):
        self.__tcattr = tcattr
        self.__backup = None

    def __setattr(self, tcattr):
        o = termios.tcgetattr(_STDIN_FD)[:]
        termios.tcsetattr(_STDIN_FD, termios.TCSANOW, tcattr)

        return o

    def __enter__(self, *args):
        self.__backup = self.__setattr(self.__tcattr)

    def __exit__(self, *args):
        self.__setattr(self.__backup)


def puts(x, y, text :str):
    print('\033[%s;%sH%s' % (y, x, text), end='')
    sys.stdout.flush()


def pprint(text :str):
    print(text, end='')
    sys.stdout.flush()


def tprint(x, y, text :str):
    pprint('\033[s')
    puts(x, y, text)
    pprint('\033[u')


def clear():
    print('\033[2J', end='')
    sys.stdout.flush()
    puts(0, 0, '')


def bgstr(text :str, bgcolor=47, tcolor=30) -> str:
    return '\033[%s;%sm%s\033[0m' % (bgcolor, tcolor, text)


def tinput(x, y, text='') -> str:
    puts(x, y, '')

    attr_o = termios.tcgetattr(_STDIN_FD)[:]
    termios.tcsetattr(_STDIN_FD, termios.TCSANOW, _TCATTR_OLD)
    
    try:
        v = input(text)
    except EOFError:
        v = None

    termios.tcsetattr(_STDIN_FD, termios.TCSANOW, attr_o)

    return v


def col() -> int:
    return os.get_terminal_size()[0]


def ln() -> int:
    return os.get_terminal_size()[1]


def show_cursor():
    tprint(0, 0, '\033[?25h')


def hide_cursor():
    tprint(0, 0, '\033[?25l')
