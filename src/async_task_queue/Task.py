
class Task(object):

    def __init__(self, main_function, callback, *args, **kwargs):
        self._main_function = main_function
        self._callback = callback
        self._args = args or tuple()
        self._kwargs = kwargs or dict()

    @property
    def callback(self):
        return self._callback

    @property
    def main_function(self):
        return self._main_function

    @property
    def args(self):
        return self._args

    @property
    def kwargs(self):
        return self._kwargs
