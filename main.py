import time

def main():
    from welcome_box import draw_welcome_box
    draw_welcome_box()
    time.sleep(0.5)

    from ui import UI
    from program_manager import ProgramManager
    from event import KeyEventQueue
    from key_reader import KeyReader

    mgr = ProgramManager('/data/data/com.termux/files/usr/bin')
    queue = KeyEventQueue()
    reader = KeyReader(queue)

    ui = UI(mgr, reader) 

    ui.main_loop()


if __name__ == '__main__':
    main()
