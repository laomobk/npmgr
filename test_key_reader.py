from event import KeyEventQueue
from key_reader import KeyReader


def main():
    queue = KeyEventQueue()
    reader = KeyReader(queue)

    reader.run()

    while True:
        t = queue.take()
        if t is not None:
            print(t)

if __name__ == '__main__':
    main()
