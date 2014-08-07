
class Function(object):

    def __init__(self, task, callback=None):
        """
        Initialize a new Function.
        :param task: The main function that will be carried out by the task.
        :param callback: The callback that will be called once the task completes.
        :return: A new Function object.
        """
        self._task = task
        self._callback = callback


    @property
    def task(self):
        """
        Get the Function's main task.
        :return: The provided task for this Function (probably a function reference object).
        """
        return self._task


    @property
    def callback(self):
        """
        Get the Function's callback.
        :return: The registered callback for this Function (probably a function reference object).
        """
        return self._callback