from threading import Thread, Lock
import termios
import os
import sys

from event import KeyEvent, KeyEventQueue
import keys

_READ_BUFFER = 5
_STDIN_FD = sys.stdin.fileno()
_ATTR_OLD = termios.tcgetattr(_STDIN_FD)[:]
_ATTR_NEW = _ATTR_OLD[:]
_ATTR_NEW[3] &= ~(termios.ICANON | termios.ECHO)

class KeyReader:
    def __init__(self, queue :KeyEventQueue):
        self.__queue = queue
        self.__keymap = {v : k
                for k, v in keys.__dict__.items() if k[:4] == 'KEY_'}
        self.__thread = None
        self.__stop = False

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
        kname = self.__keymap.get(buf, 'UNKNOWN_KEY')

        if kname == 'UNKNOWN_KEY' and buf in keys.K_MAP.keys():
            buf = keys.K_MAP.get(buf, buf)
            kname = self.__keymap.get(buf, 'UNKNOWN_KEY')

        termios.tcsetattr(_STDIN_FD, termios.TCSANOW, attr_o)

        return KeyEvent(buf, kname)

    def eat_key(self):
        os.read(_STDIN_FD, 1024)

    def stop(self, reset=True):
        self.__queue.clear()
        if reset:
            termios.tcsetattr(_STDIN_FD, termios.TCSANOW, _ATTR_OLD)
        self.__stop = True

    def continue_(self):
        self.__queue.clear()
        termios.tcsetattr(_STDIN_FD, termios.TCSANOW, _ATTR_NEW)
        self.__stop = False

    def __read_key_loop(self):
        while True:
            if self.__stop:
                continue

            k = os.read(_STDIN_FD, _READ_BUFFER)

            kname = self.__keymap.get(k, "UNKNOWN_KEY")
            
            if k == keys.KEY_RETURN:
                k = keys.KEY_ENTER

            evt = KeyEvent(k, kname)

            self.__queue.append(evt)

    def run(self):
        # set terminal attributes
        termios.tcsetattr(_STDIN_FD, termios.TCSANOW, _ATTR_NEW)

        self.__thread = Thread(target=self.__read_key_loop)
        self.__thread.setDaemon(True)
        self.__thread.start()
