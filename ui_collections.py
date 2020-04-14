# 绘制程序列表

import os
import sys
import time
import threading
import termios
import logging
import shlex

import err_screen
import easter_egg as egg

from event import KeyEvent, KeyEventQueue
from key_reader import KeyReader, _ATTR_NEW
from program_manager import ProgramManager, ProgramItem
import keys
from draw_tools import *
from constants import *

import ui_manager

from ui import UI

_LOG_PATH = 'log.log'
_USR_BIN = '/usr/bin/'
_RESOLUTION_CHECK_FREQ = 10
_STDIN_FD = sys.stdin.fileno()
_TCATTR_OLD = termios.tcgetattr(_STDIN_FD)[:]

_MIN_HEIGHT = 10
_MIN_WIDTH = 30

logging.basicConfig(filename=_LOG_PATH, filemode='w',
        level=logging.DEBUG,
        format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')

logging.info('[LOG] setup logger')


def exit(exit_code=0, cls=True):
    if cls:
        clear()
    termios.tcsetattr(_STDIN_FD, termios.TCSANOW, _TCATTR_OLD)
    sys.exit(exit_code)


class _UIWait:
    def __init__(self):
        self.__wait = False

    def __bool__(self):
        return self.__wait

    def __enter__(self, *_):
        self.__wait = True

    def __exit__(self, *_):
        self.__wait = False


class InfoBox(UI):
    _BGCOLOR = 47
    _TEXTCOLOR = 30
    _BTNBGCOLOR = 40
    _BTNTEXTCOLOR = 37
    _BTN = '[ OK ]'

    def __init__(self, msg :str, title :str):
        self.__msg = msg.split('\n')[:ln()]
        self.__title = title[:col()]

        self.__contx_height = len(self.__msg)
        self.__box_height = self.__contx_height + 3

        self.__close = False

    def __make_body_lines(self) -> str:
        title = bgstr('=' * col(),
                        self._BGCOLOR, self._TEXTCOLOR)
        
        blist = []  # body str list
        for m in self.__msg:
            mleft = int(col() / 2 - len(m) / 2) 
            mright = col() - mleft - len(m) + 2
            mstr = bgstr(' ' * mleft + m + ' ' * mright, 
                            self._BGCOLOR, self._TEXTCOLOR)
            blist.append(mstr)

        btm = bgstr('='*col(), self._BGCOLOR, self._TEXTCOLOR)

        return [title] + blist + [btm]

    def __fill_box(self):
        start_y = int(ln() / 2 - self.__contx_height / 2)

        for i in range(self.__contx_height):
            tprint(0, start_y + i, bgstr(' ' * col(), self._BGCOLOR))

    def __draw(self):
        self.__fill_box()
        
        start_y = int(ln() / 2 - self.__contx_height / 2)
        btn_y = start_y + self.__box_height - 2
        btn_start_x = int(col()/ 2 - len(self._BTN) / 2) + 1  
        title_start_x = int(col() / 2 - len(self.__title) / 2)

        strlist = self.__make_body_lines()
        
        for i, m in enumerate(strlist):
            tprint(0, start_y + i, m)

        puts(title_start_x, start_y, 
                bgstr(' %s ' % self.__title, self._BGCOLOR, self._TEXTCOLOR))
        
        puts(btn_start_x - 1, btn_y, 
                bgstr(' ' *( len(self._BTN) + 2), 
                    self._BGCOLOR, self._TEXTCOLOR))
        puts(btn_start_x, btn_y, self._BTN)

        puts(0, 0, '')

    def do_key(self, k):
        if k.key == keys.KEY_ENTER:
            ui_manager.destroy_ui(self)

    def activate(self):
        self.__draw()

    def draw(self):
        self.__draw()


class HugeTextBox(UI):
    def __init__(self, text :str, title):
        self.__text = text.split('\n')
        self.__title = title[:col()]
        self.__close = False
        self.__since = 0
    
    @property
    def __text_context_height(self):
        return col() - 2  # 2 for title and bottom 

    def __get_visible_text(self) -> list:
        return self.__text[self.__since:
                           self.__text_context_height + self.__since + 1]
    
    def __draw(self):
        clear()

        tx = int(col() / 2 - len(self.__title) / 2)

        for y, t in enumerate(self.__get_visible_text()):
            puts(0, y+1, t[:col()])

        puts(0, 0, bgstr(' '*col()))
        puts(tx, 0, bgstr(self.__title))

        puts(0, ln(), bgstr(' '*col()))

    def __close_box(self):
        ui_manager.destroy_ui(self)

    def do_key(self, k):
        if k.key in (keys.KEY_q, keys.KEY_ESC):
            self.__close_box()
        elif k.key == keys.KEY_UP:
            self.__up()
        elif k.key == keys.KEY_DOWN:
            self.__down()

    def activate(self):
        self.__draw()

    def __up(self):
        if self.__since - 1 >= 0:
            self.__since -= 1

    def __down(self):
        if self.__since + 1 < len(self.__text):
            self.__since += 1

    def draw(self):
        self.__draw()


class InputBox(UI):
    _PADDING = 3
    _BORDER = 2
    _TITLE_COLOR = (47, 30)
    _BODY_COLOR = (47, 30)
    _INPUT_AREA_COLOR = (40, 37)
    def __init__(self, title :str, prompt :str):
        self.__title = title
        self.__activated = False
        self.__input_start_y = 0
        self.__prompt = prompt

        self.__start_x = self._PADDING + 1

        self.__buffer = []
        self.__reader = KeyReader(None)

        self.__cursor_offset = 0

    @property
    def __input_length(self):
        return col() - self._PADDING * 2 - self._BORDER * 2

    @property
    def __cursor_start_x(self):
        return self._PADDING + self._BORDER

    @property
    def __max_width(self):
        return col() - self._PADDING * 2

    def __com_buffer(self, comcmd :str, ch :str):
        if comcmd == 'a' and len(self.__buffer) < self.__input_length - 1:  
            # append
            self.__buffer.insert(self.__cursor_offset, ch)
            self.__update_cursor(1)

        elif comcmd == 'd' and self.__buffer:  # delete
            self.__buffer.pop(self.__cursor_offset - 1)
            self.__update_cursor(-1)

    def __do_key(self, k):
        if k == keys.KEY_ENTER:
                puts(0, 0, '')
                self.__activated = False

        elif k in (b'\x1b[D', b'\x1b[C'):
                ofs = {b'\x1b[D' : -1, b'\x1b[C' : 1}[k]

                self.__update_cursor(ofs)

        elif len(k) == 1: # ascii input
            ok = ord(k)

            if k == b'\x7f':  # backspace
                self.__com_buffer('d', '')
                self.__rm_ch()
                self.__update_cursor()

            elif ok in range(33, 127) or k == b' ':
                self.__com_buffer('a', chr(ord(k)))

        else:
            for ch in k:
                self.__do_key(ch.to_bytes(1, 'big'))

    def __refresh(self):
        tprint(self.__cursor_start_x + 1, 
                self.__input_start_y, 
                bgstr(''.join(self.__buffer), *self._INPUT_AREA_COLOR))

        tprint(self.__cursor_start_x + 1 + len(self.__buffer) + 1, 
                self.__input_start_y, 
                bgstr('_' * (self.__input_length - len(self.__buffer) - 1), 
                    *self._INPUT_AREA_COLOR))

    def __update_cursor(self, ofs=0):
        if self.__cursor_offset + ofs in range(0, len(self.__buffer) + 1):
            self.__cursor_offset += ofs

        puts(self.__cursor_start_x + self.__cursor_offset + 1,
             self.__input_start_y, '')

    def __rm_ch(self):
        tprint(self.__cursor_start_x + len(self.__buffer) + 1,
               self.__input_start_y, ' ')

    def __key_loop(self):
        try:
            while self.__activated:
                    k = self.__reader.get_key()
                    self.__do_key(k.key)
                    self.__update_cursor()
                    self.__refresh()
        except KeyboardInterrupt:
            self.__activated = False
            self.__buffer = ['']

    def get_input(self):
        self.draw()
        # v = tinput(self.__start_x + self._BORDER, self.__input_start_y, '')
        
        self.__update_cursor()
        self.__key_loop()

        self.__activated = False
        ui_manager.destroy_ui(self)

        return ''.join(self.__buffer)

    def activate(self):
        title = self.__title
        start = int(ln() / 2) - 1
        
        tx = int(col() / 2 - len(title) / 2) - 1

        tbc, txc = self._TITLE_COLOR
        bc, tc = self._BODY_COLOR

        t1 = bgstr('=' * self.__max_width, bc)
        t2 = bgstr(' ' * self.__max_width, bc)
        t3 = '{0}{1}{0}'.format(bgstr(' ' * self._BORDER, bc),
                ' ' * (self.__max_width - self._BORDER * 2))
        t4 = t1

        for i, v in enumerate((t1, t2, t3, t4)):
            tprint(self.__start_x, start + i, v)

        tprint(self.__start_x + self._BORDER, 
                start + 1, bgstr(self.__prompt, tbc))

        tprint(tx, start, bgstr(' %s ' % title, tbc, txc))

        self.__activated = True
        self.__input_start_y = start + 2

        self.__refresh()
        self.__update_cursor()
    
    draw = activate

class Menu(UI):
    _PADDING = 1
    _BGCOLOR = 47
    _TEXTCOLOR = 30
    _HLBGCOLOR = 45
    _HLTEXTCOLOR = 37

    def __init__(self, x, y, items :list):
        self.__items = items
        self.__icur = 0
        self.__x = x
        self.__y = y
        self.__max_width = max((len(x) for x in items))
        self.__selected = None
        self.__on_select_func = None

        if self.__max_width > col() - self.__x:
            self.__max_width = col()

    @property
    def selected(self):
        return self.__selected

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    @property
    def __max_item_num(self) -> int:
        return ln() - self.__y - self._PADDING

    def __cut_string(self, text :str) -> str:
        if len(text) + self.__x > col():
            return text[:col() - self.__x]
        return text

    def __get_vis_items(self) -> list:
        start = 0
        
        if self.__icur > self.__max_item_num:
            start = self.__icur - self.__max_item_num

        return self.__items[start:self.__max_item_num + start]

    def __draw_items(self):
        vit = self.__get_vis_items()
        for i, item in enumerate(vit):
            tprint(self.__x + self._PADDING, self.__y + i, bgstr(self.__cut_string(item), 
                    self._BGCOLOR, self._TEXTCOLOR))

    def __draw_bg(self):
        total_width = self._PADDING * 2 + self.__max_width
        for yi in range(len(self.__items)):
            tprint(self.__x, self.__y + yi, bgstr(' '*total_width,
                    self._BGCOLOR))

    def __hide(self) -> int:
        return ln() - _PADDING

    def __rel_index(self) -> int:
        return self.__icur if self.__icur < len(self.__items) else len(self.__items)

    def __draw_cursor(self):
        if self.__icur > len(self.__items) or self.__icur < 0:
            return
        
        t = self.__items[self.__icur]
        total_width = self._PADDING * 2 + self.__max_width

        ty = self.__y + self.__rel_index()

        cbg = bgstr(' '*total_width, self._HLBGCOLOR, self._HLTEXTCOLOR)
        ct = bgstr(' ' * self._PADDING + str(t) + ' '*(total_width - self._PADDING - len(str(t))),
                    self._HLBGCOLOR, self._HLTEXTCOLOR)

        tprint(self.__x, ty, cbg)
        tprint(self.__x, ty, ct)

    def __is_ignore(self, item :str) -> bool:
        return item.count('-') == len(item)

    def __draw(self) -> str:
        self.__draw_bg()
        self.__draw_items()
        self.__draw_cursor()

    def do_key(self, key):
        method = {
            keys.KEY_UP:    self.__up,
            keys.KEY_DOWN:  self.__down,
            keys.KEY_ESC:   self.close_box,
            keys.KEY_ENTER: self.__select,
        }.get(key.key, lambda : logging.info('[MENU BOX] UNKNOWN KEY' + repr(key)))()

    def activate(self):
        self.__draw()

    def __up(self):
        if self.__icur - 1 < 0:
            self.__icur = len(self.__items) - 1
        else:
            self.__icur -= 1

    def __down(self):
        if self.__icur + 1 >= len(self.__items):
            self.__icur = 0
        else:
            self.__icur += 1

    def __select(self):
        if self.__is_ignore(self.__items[self.__icur]):
            return  # ignore
        self.__selected = self.__items[self.__icur]
        
        self.close_box()

        if self.__on_select_func:
            self.__on_select_func(self.__selected)

    def close_box(self):
        if self.__on_select_func:
            self.__on_select_func(None)
        ui_manager.destroy_ui(self)

    def draw(self):
        self.__draw()

    def set_on_select(self, func):
        self.__on_select_func = func


class ProgramManagerUI(UI):
    _TITLE_H = 1
    _INFO_BAR_H = 1
    _BODY_START_Y = 2
    _CONTEXT_BACK = 2
    _TITLE = 'Program Mamager'
    _MENU_BUTTON = '[M]'
    _M_BTN_A = (47, 30)
    _M_BTN_B = (40, 37)
    _BACKGROUND_COLOR = 40

    _MENU = [
             'man',
             'command',
             'search',
             'jump',
             'exec with args',
             'help',
             '---',
             'about',
             'exit',
            ]
    
    def __init__(self, mgr :ProgramManager):
        self.__mgr = mgr
        self.__items = mgr.load_programs()
        
        if not self.__items:
            self.__items = ['']

        self.__icur = 0

        self.__uiwait = _UIWait()
        self.__since_index = -1
        self.__last_since_index = -1

        self.__menu_activated = False

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
        self.__since_index = start
        
        if self.__icur > self.__item_list_height:
            start = self.__icur - self.__item_list_height
            self.__since_index = start

        end = start + self.__item_list_height

        return self.__items[start:end + 1]

    def __activates(self, ui):
        ui_manager.activate_ui(ui)

    def __cut_string(self, text :str) -> str:
        return text[:self.__col - 1]

    def __draw_items_list(self, vis_items :list):
        for i, v in enumerate(vis_items):
            ov = self.__cut_string(str(v))
            puts(0, self._BODY_START_Y + i, ov)
            print(' ' * (self.__col - len(ov)))

        if len(vis_items) < self.__item_list_height:
            print('\n'*(self.__item_list_height - len(vis_items) - 1))

    def __get_item_y(self) -> int:
        start = 0

        if self.__icur > self.__item_list_height:
            start = self.__icur - self.__item_list_height
        
        return self._BODY_START_Y + self.__icur - start

    def __draw_cursor(self):
        v = self.__items[self.__icur]
        
        tprint(0, self.__get_item_y(), bgstr(' '*self.__col, 46))
        tprint(0, self.__get_item_y(), bgstr(v, 46))

    def __draw_target(self):
        t = self.__items[self.__icur]

        tprint(0, self.__buttom_y, bgstr(' '*self.__col, 42))
        tprint(0, self.__buttom_y, bgstr('[%s] TARGET = %s'
                                % (self.__icur, str(t)), 42))

    def __draw_msg(self, msg):
        tprint(0, self.__buttom_y, bgstr(' '*self.__col, 41))
        tprint(0, self.__buttom_y, bgstr(str(msg), 41, 37))

    def __draw_input_box(self, prompt :str, title='input'):
        b = InputBox(title, prompt)
        self.__activates(b)

        return b.get_input()

    def __draw_info_box(self, msg :str, title :str):
        b = InfoBox(msg, title)
        self.__activates(b)

    def __draw_menu_button(self):
        bg, tc = self._M_BTN_B if self.__menu_activated else self._M_BTN_A
        puts(2, 0, bgstr(self._MENU_BUTTON, bg, tc))

    def __draw_background(self):
        for y in range(self.__ln + 1):
            tprint(0, y, bgstr(' '*col(), self._BACKGROUND_COLOR))

    def __draw(self):
        clear()

        hide_cursor()

        puts(0, 0, '')

        self.__draw_title()
        
        vitems = self.__get_vis_items()
        self.__draw_items_list(vitems)
        
        self.__draw_cursor()
        self.__draw_target()
        self.__draw_menu_button()

        puts(0, 0, '')
        
        show_cursor()

    def __do_menu_action(self, action :str):
        method = {
            'exit':             self.exit,
            'about':            (lambda : 
                self.__draw_info_box(CONST_ABOUT, 'ABOUT')),
            'man':              self.__man,
            'command':          self.exec_cmd,
            'search':           self.search,
            'jump':             self.jump, 
            'exec with args':   self.__select_with_arg,
            'help':             self.__help,
        }.get(action, lambda :None)()

    def do_key(self, key_event :KeyEvent):
        method = {
                
                keys.KEY_UP:        self.up,
                keys.KEY_DOWN:      self.down,
                keys.KEY_ENTER:     self.select,
                keys.KEY_EOF:       self.exit,
                keys.KEY_ALT_SPACE: self.__select_with_arg,
                keys.KEY_COLON:     self.exec_cmd,
                keys.KEY_s:         self.search,
                keys.KEY_ESC:       self.menu,
                keys.KEY_PGUP:      self.__pgup,
                keys.KEY_PGDOWN:    self.__pgdown,
                keys.KEY_m:         self.__man,
                keys.KEY_j:         self.jump,

                }.get(key_event.key, 
                        lambda : None)()

    def get_target(self):
        return self.__items[self.__icur]

    def up(self):
        if self.__icur - 1 >= 0:
            self.__icur -= 1
        else:
            self.__icur = len(self.__items) - 1
        # self.__draw()

    def down(self):
        if self.__icur + 1 < len(self.__items):
            self.__icur += 1
        else:
            self.__icur = 0
        # self.__draw()

    def __pgup(self):
        if self.__icur - self.__item_list_height < 0:
            self.__icur = 0
        else:
            self.__icur -= self.__item_list_height - 1

    def __pgdown(self):
        if self.__icur + self.__item_list_height > len(self.__items):
            self.__icur = len(self.__items) - 1
        else:
            self.__icur += self.__item_list_height + 1

    def __man(self):
        t = self.__items[self.__icur]

        self.__mgr.exec_cmd('man %s' % t, False)

    def __help(self):
        box = HugeTextBox(HELP, 'help')
        
        self.__activates(box)

    def jump(self):
        j = self.__draw_input_box('Jump to : ', 'jump')

        if j == '':
            return
        
        if j == '$':
            j = len(self.__items) - 1
        
        try:
            j = int(j)

            if j in range(0, len(self.__items)):
                self.__icur = j
            else:
                self.__draw_info_box('index out of range', 'Error')

        except (ValueError, TypeError) as e:
            self.__draw_info_box('not a valid integer :' + str(e),
                                 'Error')

    def menu(self):
        def on_select(a):
            self.__menu_activated = False
            self.__draw_menu_button()

            if a is None:
                return

            self.__do_menu_action(a)

        m = Menu(1, 2, self._MENU)
        
        self.__menu_activated = True
        self.__draw_menu_button()

        m.set_on_select(on_select)

        self.__activates(m)
 
    def search(self):
        p = self.__draw_input_box('Search pattern(RE support): ',
                                  'search')
        if not p:
            return

        i = self.__mgr.search(p)
        
        self.__icur = i if i != -1 else self.__icur

    def select(self, ask_arg=False):
        t = self.__items[self.__icur]
        
        if not t:
            return
        
        logging.info('[SEL] Selected = ' + str(t))

        arg = []

        if ask_arg:
            a = self.__draw_input_box('Arguments (Separate with space) : ')
            if not a:
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

    def exec_cmd(self):
        cmd = self.__draw_input_box('Command : ', 'command')

        if isinstance(cmd, str):
            cmd = egg.check_egg(cmd)

        if not cmd:
            return

        clear()
        
        self.__mgr.exec_cmd(cmd)

    def __select_with_arg(self):
        self.select(True)

    def exit(self):
        exit(0)

    def __main_loop0(self):
        self.__draw()
        
        try:
            while True:
                if not self.__is_valid_resolution():
                    with self.__uiwait:
                        input('Terminal to small.')
                        continue

                key = self.__reader.get_key()
                if isinstance(key, KeyEvent):
                    if key.key_name != 'UNKNOWN_KEY':
                        self.do_key(key)
                        self.__draw()
                    else:
                        self.__draw_msg('Unknown input: ' + repr(key.key))
        except KeyboardInterrupt as e:
            clear()
            print(str(e))
            exit(1, False)

        # time.sleep(1 / _REFRESH_RATE)

    def activate(self):
        self.__draw()

    def draw(self):
        self.__draw()

    def main_loop(self):
        ui_manager.activate_ui(self, self)
        # self.__init_loop()

    def __init_loop(self):
        try:
            self.__main_loop0()
        except Exception:
            with self.__uiwait:
                err_screen.handle_exception(*sys.exc_info())

    def test(self, cur=0):
        self.__icur = cur
        self.__draw()


if __name__ == '__main__':
    queue = KeyEventQueue()
    reader = KeyReader(queue)
    mgr = ProgramManager('/data/data/com.termux/files/usr/bin')
    ui = UI(mgr, reader)

    ui.main_loop()
