from copy import copy
from threading import RLock, Thread
import traceback


class Queue(object):

    def __init__(self, parallelism):
        """
        Create a new Queue that will process tasks asynchronously.
        :param parallelism: The number of simultaneous workers that will be used to process tasks.
        :return: A new Queue object.  If paralellism < 1, raise ValueError.
        """
        if parallelism < 1:
            raise ValueError('Parallelism may not be less than 1.')

        self._is_running = False
        self._parallelism = parallelism

        self._lock = RLock()

        self._tasks = list()
        self._tasks_for_next_run = list()
        self._tasks_in_flight = 0

        self._callbacks = list()
        self._callbacks_for_next_run = list()


    # API #
    def size(self):
        """
        Get the number of queued tasks that have not been started yet.
        :return: An integer that specifies the number of tasks queued in the task async_task_queue.
        """
        with self._lock:
            return len(self._tasks)


    def is_running(self):
        """
        Get the running status of the async_task_queue.
        :return: A boolean value specifying whether the async_task_queue has been started or not.
        """
        with self._lock:
            return self._is_running


    def in_flight(self):
        """
        Get the number of tasks currently being run by workers.
        :return: An integer that specifies the number of tasks currently under processing by workers.
        """
        with self._lock:
            return self._tasks_in_flight


    def add_task(self, task):
        """
        Add a task to the async_task_queue of tasks to process.
        :param task: The task to be added for execution.
        :return: Nothing.
        """
        with self._lock:
            if not self.is_running():
                self._tasks.append(task)
            else:
                print('Warning: task added while async_task_queue was running.  It has been added to a list and will be executed '
                      'after the next call to `start`.')
                self._tasks_for_next_run.append(task)


    def add_callback(self, callback):
        """
        Add a callback that will be executed when all the tasks have been processed.
        :param callback: A function that receives the async_task_queue object.
        :return: Nothing.
        """
        with self._lock:
            if not self.is_running():
                self._callbacks.append(callback)
            else:
                print('Warning: callback added while task queue was running.  It has been registered and will be '
                      'added to the next run.')
                self._callbacks_for_next_run.append(callback)


    def start(self):
        """
        Start executing tasks.
        :return: Nothing.
        """
        if not self.is_running():
            self._reset_tasks()
            self._reset_callbacks()
            self._is_running = True
            self._start_worker_threads()


    # Internal methods #

    def _reset_tasks(self):
        self._tasks_for_next_run.extend(self._tasks)
        self._tasks = self._tasks_for_next_run
        self._tasks_for_next_run = list()


    def _reset_callbacks(self):
        self._callbacks_for_next_run.extend(self._callbacks)
        self._callbacks = self._callbacks_for_next_run
        self._callbacks_for_next_run = list()


    def _start_worker_threads(self):
        """
        Start `self.parallelism` threads to start processing tasks.
        :return: Nothing.
        """
        self._worker_threads = list()
        for thread_num in range(0, self._parallelism):
            worker_thread = Thread(target=self._process_tasks)
            worker_thread.start()


    def _process_tasks(self):
        """
        Start a loop of performing tasks until none are available.
        :return: Nothing.
        """
        do_work = True
        while do_work:
            try:
                task = self._pop_task()
                self._run_task(task)
                self._finish_task()
            except IndexError:
                do_work = False

            with self._lock:
                if self._check_if_all_tasks_done():
                    self._finish_queue_run()


    def _pop_task(self):
        """
        Retrieve a task from the top of the async_task_queue.
        :return: Nothing.
        """
        with self._lock:
            task = self._tasks.pop(0)
            self._tasks_in_flight += 1
        return task


    def _run_task(self, task):
        """
        Run a Function object as a task.
        :param task: The Function object which will be run.
        :return: Nothing.
        """
        self._sandbox_run(task.task)
        self._sandbox_run(task.callback)


    def _sandbox_run(self, function, *args, **kwargs):
        """
        Run a function in a simple sandbox.
        :param function: The function which will be run.
        :param args: The argument tuple that will be provided as argument to the function.
        :param kwargs: The keyword argument dict that will be provided to the function.
        :return: Nothing.
        """
        try:
            function(*args, **kwargs)
        except:
            self._log_exception()


    def _log_exception(self):
        """
        Print an exception traceback to stdout, as a mechanism for notification of exceptions in the processing of
        the async_task_queue.
        :return:
        """
        print('Exception raised: %s' % traceback.format_exc())


    def _finish_task(self):
        """
        Mark a task as finished.
        :return: Nothing.
        """
        with self._lock:
            self._tasks_in_flight -= 1


    def _check_if_all_tasks_done(self):
        """
        Check the async_task_queue and see if all tasks are done (i.e. it is still running, no tasks are in flight and if
        no tasks are accumulated tasks.
        :return: A boolean value specifying whether all tasks are done or not.
        """
        with self._lock:
            if self.is_running() and self.in_flight() == 0 and self.size() == 0:
                return True
            return False


    def _finish_queue_run(self):
        """
        Finish the current async_task_queue run.  Execute all the registered callbacks for on_finish.
        :return: Nothing.
        """
        with self._lock:

            while True:
                try:
                    callback = self._callbacks.pop(0)
                    self._sandbox_run(callback, self)
                except IndexError:
                    break

            self._is_running = False