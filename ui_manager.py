import threading

import logging
from key_reader import KeyReader
from event import KeyEventQueue
from ui import UI
import exceptions
from err_screen import handle_exception
import sys
from draw_tools import clear, ln, col
import time
import ui_share


_RESOLUTION_CHECK_FREQ = 10
_DRAW_ALL_UI_EACH_REFRESH = True  


class _UIManager:
    def __init__(self):
        self.__ui_stack = []
        self.__queue = KeyEventQueue()
        self.__kreader = KeyReader(self.__queue)
    
    @property
    def __current_ui(self) -> UI:
        return self.__ui_stack[-1]  \
                if self.__ui_stack else None

    def __check_and_append_ui(self, ui):
        if not isinstance(ui, UI):
            raise exceptions.NotAnUIException('%s is not an UI instance' % ui)
        self.__ui_stack.append(ui)

    def __check_resolution(self):
        oc, ol = col(), ln()

        while True:
            if (oc != col() or ol != ln()) and not ui_share.CMD_MODE:
                oc, ol = col(), ln()
                self.__draw()

            time.sleep(1 / _RESOLUTION_CHECK_FREQ)

    def __do_key(self):
        k = self.__kreader.get_key()
        self.__current_ui.do_key(k)

    def __draw_current_ui(self):
        self.__current_ui.draw()

    def __draw(self):
        if _DRAW_ALL_UI_EACH_REFRESH:
            self.draw_all_ui()
        else:
            self.__draw_current_ui()

    def draw_all_ui(self):
        clear()
        for ui in self.__ui_stack:
            ui.draw()

    def get_current_ui(self):
        return self.__current_ui.cur_ui

    def activate_ui(self, ui):
        self.draw_all_ui()
        self.__check_and_append_ui(ui)
        ui.activate()

    def destroy_ui(self, ui):
        if ui in self.__ui_stack:
            self.__ui_stack.remove(ui)
            self.__draw_current_ui()

    def main_loop(self):
        t = threading.Thread(target=self.__check_resolution)
        t.setDaemon(True)
        t.start()

        try:
            while True:
                self.__do_key()
                self.__draw_current_ui()
        except KeyboardInterrupt:
            main_loop()  # ignore

        except Exception:
            handle_exception(*sys.exc_info())

    def exit(self, exit_code=0):
        clear()
        sys.exit(exit_code)


GLOBAL_BOX_MANAGER = _UIManager()


def activate_ui(ui):
    GLOBAL_BOX_MANAGER.activate_ui(ui)


def destroy_ui(ui):
    GLOBAL_BOX_MANAGER.destroy_ui(ui)


def get_current_ui():
    return GLOBAL_BOX_MANAGER.get_current_ui()


def main_loop():
    GLOBAL_BOX_MANAGER.main_loop()


def refresh_screen():
    GLOBAL_BOX_MANAGER.draw_all_ui()


def npmgr_exit(exit_code=0):
    GLOBAL_BOX_MANAGER.exit(exit_code)


