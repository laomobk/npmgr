import os
import re

class ProgramItem:
    def __init__(self, name, path):
        self.__name = name
        self.__path = path

    @property
    def name(self):
        return self.__name

    @property
    def path(self):
        return self.__path

    def __str__(self) -> str:
        return '%s' % self.__name

    __repr__ = __str__


class ProgramManager:
    def __init__(self, path='/usr/bin/'):
        self.__path = path
        self.__programs = []

    def __load_programs(self, path) -> list:
        d = os.listdir(self.__path)
        
        for item in d:
            itemp = os.path.join(path, item)
            if not os.path.isdir(itemp):
                self.__programs.append(
                        ProgramItem(item, itemp))

        return self.__programs

    def load_programs(self) -> list:
        return self.__load_programs(self.__path)

    def exec(self, prog :ProgramItem, *args):
        p = prog.path
        
        os.system(' '.join((p,) + args))

        input('\n[Press Enter to exit]')

    def search(self, pattern :str) -> int:
        ro = re.compile(pattern)

        for i, v in enumerate(self.__programs):
            if ro.match(v.name):
                return i
        return -1
