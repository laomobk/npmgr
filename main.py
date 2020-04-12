import time
import sys

_TERMUX_BIN = '/data/data/com.termux/files/usr/bin'

def main():
    import err_screen
    try:
        from welcome_box import draw_welcome_box
        draw_welcome_box()
        # time.sleep(0.5)

        from ui import UI
        from program_manager import ProgramManager
        from event import KeyEventQueue
        from key_reader import KeyReader
        
        mgr = ProgramManager(_TERMUX_BIN
                            )
        queue = KeyEventQueue()
        reader = KeyReader(queue)

        ui = UI(mgr, reader) 

        ui.main_loop()
    except Exception:
        err_screen.handle_exception(*sys.exc_info())


if __name__ == '__main__':
    main()
