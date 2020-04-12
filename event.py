from threading import Lock


class KeyEvent:
    def __init__(self, key :int, key_name :str):
        self.__key = key
        self.__key_name = key_name

    @property
    def key(self):
        return self.__key

    @property
    def key_name(self):
        return self.__key_name

    def __repr__(self) -> str:
        return 'KEY = %s (%s)' % (self.__key_name, self.key)

    __str__ = __repr__


class KeyEventQueue:
    def __init__(self):
        self.__lock = Lock()
        self.__queue = []

    def append(self, kevt :KeyEvent):
        try:
            self.__lock.acquire()
            self.__queue.append(kevt)
        except:
            raise
        finally:
            if self.__lock.locked():
                self.__lock.release()

    def take(self) -> KeyEvent:
        try:
            self.__lock.acquire()
            v = self.__queue.pop(0) if self.__queue else None
        except:
            raise
        finally:
            if self.__lock.locked():
                self.__lock.release()

        return v

    def clear(self):
        self.__queue.clear()
