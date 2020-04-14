import os
import re
import logging

import ui_share
import draw_tools


class _CMDModeContext:
    def __init__(self):
        self.__omode = False
        self.__tcctx = draw_tools.TcAttrContext(draw_tools.TCATTR_COMMON)

    def __enter__(self, *_):
        self.__tcctx.__enter__()
        self.__omode = ui_share.CMD_MODE
        ui_share.CMD_MODE = True

    def __exit__(self, *_):
        self.__tcctx.__exit__()
        ui_share.CMD_MODE = self.__omode


run_command = _CMDModeContext()


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
        logging.info('[PLOADER] Load path = %s' % path)

        if not os.path.exists(path) or not os.path.isdir(path):
            logging.info('Path \'%s\' is invalid' % path)
            return []

        d = os.listdir(path)
        
        for item in d:
            itemp = os.path.join(path, item)
            if not os.path.isdir(itemp):
                self.__programs.append(
                        ProgramItem(item, itemp))

        return self.__programs

    def load_programs(self, path :str=None) -> list:
        p = path if path else self.__path
        return self.__load_programs(p)

    def exec(self, prog :ProgramItem, *args):
        p = prog.path
        
        with run_command:
            os.system(' '.join((p,) + args))

            input('\n[Press Enter to exit]')

    def search(self, pattern :str) -> int:
        ro = re.compile(pattern)

        for i, v in enumerate(self.__programs):
            if ro.match(v.name):
                return i
        return -1

    def exec_cmd(self, cmd, wait=True):
        with run_command:
            os.system(cmd)
            
            if wait:
                input('\n[Press Enter to exit]')
