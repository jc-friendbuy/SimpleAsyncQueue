from threading import Thread


class Worker(object):
    """
    Simple thread wrapper object that fetches tasks from a task queue and publishes events (mainly callbacks) to an
    event loop.
    """

    def __init__(self, queue, main_event_loop):
        """
        Initialize the worker.
        :param queue: The task queue that will be used to publish tasks.
        :param main_event_loop: The event loop that will be used for publishing callbacks.
        :return: A new Worker instance.
        """
        self._queue = queue
        self._thread = None
        self._main_event_loop = main_event_loop

    def start(self):
        """
        Start point for executing work.  This launches a new thread and begins the main work loop.
        :return: Nothing.
        """
        self._thread = Thread(target=self._work)

    def _work(self):
        """
        The main work function.  Loop while there are tasks in the queue, fetching end performing them. Finally,
        exit when there are no tasks left.
        :return: Nothing.
        """
        do_work = True
        while do_work:
            try:
                self._perform_task(self._queue.get_task())
            except IndexError:
                do_work = False
                self._finish_processing_if_not_finished_already()
        print('Thread %s is exiting now.' % self._thread.name)

    def _perform_task(self, task):
        """
        Execute a task, adding its callback to the main event loop if one is defined.
        :param task: The task to perform.
        :return: Nothing.
        """
        self._queue.task_started()
        try:
            task.execute()
            if task.callback:
                self._main_event_loop.publish(task.callback)
        except:
            # TODO probably log here
            pass
        finally:
            self._queue.task_finished()

    def _finish_processing_if_not_finished_already(self):
        """
        Query the queue for the end of processing, and if done, notify it to finish.
        :return: Nothing.
        """
        if self._queue.get_should_finish():
            self._queue.finish()
