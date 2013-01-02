import functools
from decorator import decorator

__author__ = 'Dean Gardiner'


class NotSupportedError(BaseException):
    pass


class SupportBase():
    """SupportBase

    :param force: Force functions to be supported
    """
    def __init__(self, force=False):
        self.supportedFunctions = []
        self.force = force

    def isSupported(self, name):
        """Is function supported (by name)?

        :param name: Function Name
        """
        return (name in self.supportedFunctions) or self.force

    def isFunctionSupported(self, function):
        """Is function supported (by function reference)?

        :param function: Function Reference

        :raises: :class:`ircc.InvalidArgumentError`
        """
        if not isinstance(function, functools.partial):
            raise NotSupportedError()
        return self.isSupported(function.args[0].f.__name__)


@decorator
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