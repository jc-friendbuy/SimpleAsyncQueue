
class Task(object):
    """
    Simple task class that wraps a function (with arguments and keyword arguments) and a callback.
    """

    def __init__(self, main_function, callback, *args, **kwargs):
        """
        Initialize a simple task with a callback.
        :param main_function: The main function of the task.
        :param callback: The callback that is to be called after the task is done.
        :param args: An argument list for the main_function.
        :param kwargs: A keyword argument dictionary for the main function.
        :return: A new Task object.
        """
        self._main_function = main_function
        self._callback = callback
        self._args = args or tuple()
        self._kwargs = kwargs or dict()

    def execute(self):
        """
        Run the main function with the arguments and keyword arguments provided.
        :return: The return value of the main function defined for this task.
        """
        return self._main_function(*self._args, **self._kwargs)

    @property
    def callback(self):
        """
        Property for the callback of the function.
        :return: The callback defined for this Task.
        """
        return self._callback
