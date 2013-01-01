import functools
import inspect

__author__ = 'Dean Gardiner'


class NotSupportedError(BaseException):
    pass


class SupportBase():
    def __init__(self):
        self.supportedFunctions = []

    def isSupported(self, name):
        return name in self.supportedFunctions

    def isFunctionSupported(self, function):
        if not isinstance(function, functools.partial):
            raise Exception()
        return self.isSupported(function.args[0].f.__name__)


class supported(object):
    def __init__(self, f):
        self.f = f

    def __call__(self, dec, *args, **kwargs):
        if not isinstance(args[0], SupportBase):
            raise NotSupportedError()

        if not self.f.__name__ in args[0].supportedFunctions:
            raise NotSupportedError()

        return self.f(*args, **kwargs)

    def __get__(self, instance, owner):
        return functools.partial(self.__call__, self, instance)