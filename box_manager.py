import threading

import logging
from key_reader import KeyReader
from event import KeyEventQueue
from ui import UI
import exceptions
from err_screen import handle_exception
import sys
from draw_tools import clear

class _CurUI:
    cur_ui = None


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

    def __do_key(self):
        k = self.__kreader.get_key()
        self.__current_ui.do_key(k)

    def __draw_current_ui(self):
        self.__current_ui.draw()

    def get_current_ui(self):
        return self.__current_ui.cur_ui

    def activate_ui(self, ui):
        self.__check_and_append_ui(ui)
        ui.activate()

    def destroy_ui(self, ui):
        if ui in self.__ui_stack:
            self.__ui_stack.remove(ui)
            self.__draw_current_ui()

    def main_loop(self):
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


def npmgr_exit(exit_code=0):
    GLOBAL_BOX_MANAGER.exit(exit_code)

