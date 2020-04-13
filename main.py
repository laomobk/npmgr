import time
import sys
import os

_TERMUX_BIN = '/data/data/com.termux/files/usr/bin'
_MIN_COL = 30
_MIN_LN = 20


def check_os():
    if os.name == 'posix':
        return
    raise Exception('NPMGR only running on UNIX system')


def check_resolution():
    import draw_tools as draw

    if draw.col() < _MIN_COL or draw.ln() < _MIN_LN:
        raise Exception('NPMGR have to running in a terminal which is over %sx%s'
            % (_MIN_COL, _MIN_LN))


def main():
    import err_screen
    from box_manager import activate_ui, main_loop, npmgr_exit
    try:
        check_os()

        from welcome_box import draw_welcome_box
        draw_welcome_box()
        # time.sleep(0.5)

        from ui_collections import ProgramManagerUI
        from program_manager import ProgramManager
        from event import KeyEventQueue
        from key_reader import KeyReader
        
        mgr = ProgramManager(_TERMUX_BIN
                             )

        queue = KeyEventQueue()
        reader = KeyReader(queue)

        ui = ProgramManagerUI(mgr)

        activate_ui(ui)

        main_loop()

    except KeyboardInterrupt:
        pass
    except Exception:
        err_screen.handle_exception(*sys.exc_info())


if __name__ == '__main__':
    main()
