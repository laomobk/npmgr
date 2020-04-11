# 绘制程序列表

import os
import sys
import time

_USR_BIN = '/usr/bin/'


def _puts(x, y, text :str):
    print('\033[%s;%sH%s' % (y, x, text), end='')
    sys.stdout.flush()


def _pprint(text :str):
    print(text, end='')
    sys.stdout.flush()


def _tprint(x, y, text :str):
    _pprint('\033[s')
    _puts(x, y, text)
    _pprint('\033[u')


def _clear():
    print('\033[2J', end='')


def _bgstr(text :str, bgcolor=47, tcolor=30) -> str:
    return '\033[%s;%sm%s\033[0m' % (bgcolor, tcolor, text)


class UI:
    _TITLE_H = 1
    _INFO_BAR_H = 1
    _BODY_START_Y = 2
    _CONTEXT_BACK = 2
    _TITLE = 'Program Mamager'
    
    def __init__(self, items :list):
        self.__items = items
        self.__icur = 0

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

    def __draw_title(self):
        pos = int(self.__col / 2 - len(self._TITLE) / 2)
        _puts(0, 0, _bgstr(' ' * self.__col))  # Draw background bar
        _tprint(pos, 0, _bgstr(self._TITLE))
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
            _puts(0, self._BODY_START_Y + i, self.__cut_string(str(v)))
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
        
        _tprint(0, self.__get_item_y(), _bgstr(' '*self.__col, 46))
        _tprint(0, self.__get_item_y(), _bgstr(v, 46))

    def __draw_target(self):
        t = self.__items[self.__icur]

        _tprint(0, self.__buttom_y, _bgstr(' '*self.__col, 42))
        _tprint(0, self.__buttom_y, _bgstr('TARGET = ' + str(t), 42))

    def __draw(self):
        _clear()
        self.__draw_title()
        self.__draw_items_list(self.__get_vis_items())
        self.__draw_curser()
        self.__draw_target()

        _puts(0, 0, "")

    def up(self):
        if self.__icur - 1 >= 0:
            self.__icur -= 1
        self.__draw()

    def down(self):
        if self.__icur + 1 < len(self.__items):
            self.__icur += 1
        self.__draw()

    def get_target(self):
        return self.__items[self.__icur]

    def test(self, cur=0):
        self.__icur = cur
        self.__draw()


if __name__ == '__main__':
    ui = UI(['Nezha%s' % i for i in range(100)])

    for i in range(10):
        ui.down()
        time.sleep(0.5)
    
    ui.test(0)

    input()
