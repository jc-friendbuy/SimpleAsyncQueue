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
        self._parallelism = parallelism

        self._is_running = False
        self._lock = RLock()
        self._tasks = list()
        self._tasks_for_next_run = list()
        self._on_finish_callbacks = list()
        self._tasks_in_flight = 0
        self._worker_threads = None


    # Object API #
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
        :param task:
        :return: Nothing.
        """
        with self._lock:
            if not self.is_running():
                self._tasks.append(task)
            else:
                # TODO
                print('Warning: task added while async_task_queue was running.  It has been added to a list and will be executed '
                      'after the next call to `start`.')

    def add_callback(self, callback):
        """
        Add a callback that will be executed when all the tasks have been processed.
        :param callback: A function that receives the async_task_queue object.
        :return: Nothing.
        """
        with self._lock:
            self._on_finish_callbacks.append(callback)

    def start(self):
        """
        Start executing tasks.
        :return: Nothing.
        """
        if not self.is_running():
            self._tasks.extend(self._tasks_for_next_run)
            self._tasks_for_next_run = list()
            self._is_running = True
            self._start_worker_threads()


    # Implementing private functions #
    def _start_worker_threads(self):
        """
        Start `self.parallelism` threads to start processing tasks.
        :return: Nothing.
        """
        self._worker_threads = list()
        for thread_num in xrange(0, self._parallelism):
            self._worker_threads.append(Thread(target=self._process_tasks))


    def _process_tasks(self):
        """
        Start a loop of performing tasks until none are available.
        :return: Nothing.
        """
        while True:
            try:
                task = self._pop_task()
            except IndexError:
                break

            # TODO: How does the callback work here?
            self._safely_run_function(task.main_function, *task.args, **task.kwargs)
            self._safely_run_function(task.callback)
            self._finish_task()


    def _pop_task(self):
        """
        Retrieve a task from the top of the async_task_queue.
        :return: Nothing.
        """
        with self._lock:
            task = self._tasks.pop()
            self._tasks_in_flight += 1
        return task


    def _finish_task(self):
        """
        Mark a task as finished and then check if processing is done to finish the current async_task_queue run.
        :return: Nothing.
        """
        with self._lock:
            self._tasks_in_flight -= 1

        if self._check_if_all_tasks_done():
            self._finish_queue_run()


    def _check_if_all_tasks_done(self):
        """
        Check the async_task_queue and see if all tasks are done (i.e. it is still running, no tasks are in flight and if
        no tasks are accumulated tasks.
        :return: A boolean value specifying whether all tasks are done or not.
        """
        with self._lock:
            if self.is_running() and self.in_flight() == 0 and self.size() == 0:
                self._is_running = False
                return True
        return False


    def _finish_queue_run(self):
        """
        Finish the current async_task_queue run.  Execute all the registered callbacks for on_finish.
        :return: Nothing.
        """
        while True:
            try:
                callback = self._on_finish_callbacks.pop()
            except IndexError:
                break
            self._safely_run_function(callback, self)

    def _safely_run_function(self, function, *args, **kwargs):
        """
        Run a generic callback, wrapped in a try-except which prints out errors.  The purpose of this is to provide a
        secure environment for callbacks to be run, so that async_task_queue processing is not interrupted by exceptions.
        :param function: The callback function to be run.
        :param args: The arguments for the callback.
        :param kwargs: The keyword arguments for the callback.
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

