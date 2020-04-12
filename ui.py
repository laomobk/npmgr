# 绘制程序列表

import os
import sys
import time
import threading
import termios
import logging
import shlex

from event import KeyEvent, KeyEventQueue
from key_reader import KeyReader, _ATTR_NEW
from program_manager import ProgramManager, ProgramItem
import keys
from draw_tools import *

_LOG_PATH = 'log.log'
_USR_BIN = '/usr/bin/'
_RESOLUTION_CHECK_FREQ = 10
_STDIN_FD = sys.stdin.fileno()
_TCATTR_OLD = termios.tcgetattr(_STDIN_FD)[:]

_MIN_HEIGHT = 10
_MIN_WIDTH = 30

_INPUT_TITLE = 'NOTICE'

logging.basicConfig(filename=_LOG_PATH, filemode='w',
        level=logging.DEBUG,
        format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')

logging.info('[LOG] setup logger')


class UIDrawTask:
    def __init__(self, target, *args):
        self.__target = target
        self.__args = args

    def draw(self):
        self.__target(*args)


class _UIWait:
    def __init__(self):
        self.__wait = False

    def __bool__(self):
        return self.__wait

    def __enter__(self, *_):
        self.__wait = True

    def __exit__(self, *_):
        self.__wait = False


class Memu:
    _PADDING = 1
    def __init__(self, x, y, items :list, reader :KeyReader):
        self.__items = items
        self.__icur = 0
        self.__x = x
        self.__y = y
        self.__max_width = max((len(x) for x in items))

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    def __get_vis_items(self) -> list:
        return self.__items[self.y:ln() - self._PADDING]

    def __draw_items(self):
        vit = self.__get_vis_items()
        

    def __draw_memu(self):
        total_width = self._PADDING * 2 + self.__max_width

    def draw(self) -> str:
        pass


class UI:
    _TITLE_H = 1
    _INFO_BAR_H = 1
    _BODY_START_Y = 2
    _CONTEXT_BACK = 2
    _TITLE = 'Program Mamager'
    
    def __init__(self, mgr :ProgramManager, reader :KeyReader):
        self.__mgr = mgr
        self.__items = mgr.load_programs()
        self.__icur = 0
        self.__reader = reader

        self.__uiwait = _UIWait()

    @property
    def __col(self) -> int:
        return os.get_terminal_size()[0]

    @property
    def __ln(self) -> int:
        return os.get_terminal_size()[1]

    @property
    def __item_list_height(self) -> int:
        return self.__ln - self._CONTEXT_BACK - 1

    @property
    def __buttom_y(self) -> int:
        return self.__col - 1

    def __is_valid_resolution(self) -> bool:
        return self.__col > _MIN_WIDTH and self.__ln > _MIN_HEIGHT

    def __draw_title(self):
        pos = int(self.__col / 2 - len(self._TITLE) / 2)
        puts(0, 0, bgstr(' ' * self.__col))  # Draw background bar
        tprint(pos, 0, bgstr(self._TITLE))
        print()

    def __get_vis_items(self) -> list:
        start = 0
        
        if self.__icur > self.__item_list_height:
            start = self.__icur - self.__item_list_height

        end = start + self.__item_list_height

        return self.__items[start:end + 1]

    def __cut_string(self, text :str) -> str:
        return text[:self.__col - 1]

    def __draw_items_list(self, vis_items :list):
        for i, v in enumerate(vis_items):
            puts(0, self._BODY_START_Y + i, self.__cut_string(str(v)))
            print()

        if len(vis_items) < self.__item_list_height:
            print('\n'*(self.__item_list_height - len(vis_items) - 1))

    def __get_item_y(self) -> int:
        start = 0

        if self.__icur > self.__item_list_height:
            start = self.__icur - self.__item_list_height
        
        return self._BODY_START_Y + self.__icur - start

    def __draw_curser(self):
        v = self.__items[self.__icur]
        
        tprint(0, self.__get_item_y(), bgstr(' '*self.__col, 46))
        tprint(0, self.__get_item_y(), bgstr(v, 46))

    def __draw_target(self):
        t = self.__items[self.__icur]

        tprint(0, self.__buttom_y, bgstr(' '*self.__col, 42))
        tprint(0, self.__buttom_y, bgstr('TARGET = ' + str(t), 42))

    def __draw_msg(self, msg):
        tprint(0, self.__buttom_y, bgstr(' '*self.__col, 41))
        tprint(0, self.__buttom_y, bgstr(str(msg), 41, 37))

    def __draw_input_box(self, prompt :str):
        start = int(self.__ln / 2) - 1
        
        tleft = int(self.__col / 2 - len(_INPUT_TITLE) / 2) - 1
        tright = self.__col - (tleft + len(_INPUT_TITLE)) - 1

        t1 = bgstr('=' * tleft + _INPUT_TITLE + ' ' + '=' * tright, 41)
        t2 = ' ' * self.__col
        t3 = bgstr('=' * self.__col, 41)

        for i, v in enumerate((t1, t2, t3)):
            tprint(0, start + i, v)
        
        with self.__uiwait:
            return tinput(0, start + 1, bgstr(prompt, 41))

    def __draw(self):
        clear()

        if not self.__is_valid_resolution():
            print('Terminal to small.')
            return

        self.__draw_title()
        self.__draw_items_list(self.__get_vis_items())
        self.__draw_curser()
        self.__draw_target()

        puts(0, 0, "")

    def __do_key(self, key_event :KeyEvent):
        method = {
                keys.KEY_UP:        self.up,
                keys.KEY_DOWN:      self.down,
                keys.KEY_ENTER:     self.select,
                keys.KEY_EOF:       self.exit,
                keys.KEY_ALT_SPACE: self.__select_with_arg,
                keys.KEY_COLON:     self.__exec_cmd,
                }.get(key_event.key, 
                        lambda : None)()

    def __check_resolution(self):
        oc, ol = self.__col, self.__ln

        while True:
            if (self.__col != oc or self.__ln != ol) and not self.__uiwait:
                self.__draw()
                oc, ol = self.__col, self.__ln

            time.sleep(1 / _RESOLUTION_CHECK_FREQ)

    def up(self):
        if self.__icur - 1 >= 0:
            self.__icur -= 1
        self.__draw()

    def down(self):
        if self.__icur + 1 < len(self.__items):
            self.__icur += 1
        self.__draw()

    def select(self, ask_arg=False):
        t = self.__items[self.__icur]
        logging.info('[SEL] Selected = ' + str(t))

        arg = []

        if ask_arg:
            a = self.__draw_input_box('Arguments (Separate with space) : ')
            if a is None:
                return
            arg = shlex.split(a)

        try:
            self.__draw_msg('Press Enter twice to run.')

            clear()

            with self.__uiwait:
                self.__mgr.exec(t, *arg)

            logging.info('[SEL] Finish')
        except Exception as e:
            logging.info('[SEL] Exception raised : ' + str(e))
            raise KeyboardInterrupt(str(e))

    def __exec_cmd(self):
        cmd = self.__draw_input_box('Command : ')

        if not cmd:
            return

        clear()
        os.system(cmd)

        input('\n[Press enter to exit]')

    def __select_with_arg(self):
        self.select(True)

    def exit(self):
        clear()
        sys.exit(0)

    def get_target(self):
        return self.__items[self.__icur]

    def main_loop(self):
        ch_thread = threading.Thread(target=self.__check_resolution)
        ch_thread.setDaemon(True)
        ch_thread.start()

        self.__draw()

        try:
            while True:
                key = self.__reader.get_key()
                if isinstance(key, KeyEvent):
                    if key.key_name != 'UNKNOWN_KEY':
                        self.__do_key(key)
                        self.__draw()
                    else:
                        self.__draw_msg('Unknown input')
        except KeyboardInterrupt as e:
            clear()
            print(str(e))
            sys.exit(0)

        # time.sleep(1 / _REFRESH_RATE)

    def test(self, cur=0):
        self.__icur = cur
        self.__draw()


if __name__ == '__main__':
    queue = KeyEventQueue()
    reader = KeyReader(queue)
    mgr = ProgramManager('/data/data/com.termux/files/usr/bin')
    ui = UI(mgr, reader)

    ui.main_loop()
