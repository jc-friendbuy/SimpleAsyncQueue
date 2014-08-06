from threading import Lock, Thread, Condition
import time


class EventLoop(object):

    def __init__(self):
        self._events = list()
        self._thread = None
        self._lock = Lock()
        self._event_ready_condition = Condition(lock=self._lock)



    def publish(self, event):
        with self._lock:
            self._events.append(event)

    def start(self):
        self._thread = Thread(target=self._process_events)

    def _process_events(self):
        do_process = True
        while do_process:
            with self._event_ready_condition as event_ready:
                if event_ready.wait_for(len(self._events) > 0, timeout=0.01):






