from queue import Queue

class EventBus:
    def __init__(self):
        self._event_queue = Queue()

    def _get_event(self) -> tuple:
        '''
        :return (event_code, *event_arg)
        '''
        if self._event_queue.empty():
            return (0, None)  # Nop Event
        return self._event_queue.get_nowait()

    def _add_event(self, event_code, *event_args):
        self._event_queue.put((event_code, event_args))
