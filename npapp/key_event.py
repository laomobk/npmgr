from threading import Lock


class KeyEvent:
    def __init__(self, key :int):
        self.__key = key

    @property
    def key(self):
        return self.__key

    def __repr__(self) -> str:
        return 'KEY = %s' % self.__key

    __str__ = __repr__


