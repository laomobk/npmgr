import termios
import os
import sys

from key_event import KeyEvent

_READ_BUFFER = 5
_STDIN_FD = sys.stdin.fileno()
_ATTR_OLD = termios.tcgetattr(_STDIN_FD)[:]
_ATTR_NEW = _ATTR_OLD[:]
_ATTR_NEW[3] &= ~(termios.ICANON | termios.ECHO)

class KeyReader:
    def wait_key(self, key):
        attr = termios.tcgetattr(_STDIN_FD)[:]
        termios.tcsetattr(_STDIN_FD, termios.TCSANOW, _ATTR_NEW)

        k = -5

        while k != key:
            k = os.read(_STDIN_FD, 1)

        termios.tcsetattr(_STDIN_FD, termios.TCSANOW, attr)

    def get_key(self) -> KeyEvent:
        attr_o = termios.tcgetattr(_STDIN_FD)
        termios.tcsetattr(_STDIN_FD, termios.TCSANOW, _ATTR_NEW)
        
        buf = os.read(_STDIN_FD, _READ_BUFFER)

        termios.tcsetattr(_STDIN_FD, termios.TCSANOW, attr_o)

        return KeyEvent(buf)

    def eat_key(self):
        os.read(_STDIN_FD, 1024)

