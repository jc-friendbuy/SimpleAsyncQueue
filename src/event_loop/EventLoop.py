from threading import Lock
import time


class EventLoop(object):

    def __init__(self):
        self._lock = Lock()
        self._events = list()

    def publish(self, event):
        with self._lock:
            self._events.append(event)

    def start(self):
        while True:
            with self._lock:
                try:
                    self._process_event(self._events.pop())
                except IndexError:
                    time.sleep(0,1)



