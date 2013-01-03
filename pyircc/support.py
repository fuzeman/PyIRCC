from pyircc.spec import InvalidFunctionError, NotSupportedError

__author__ = 'Dean Gardiner'


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

        :raises: :class:`support.InvalidFunctionError`
        """
        if not hasattr(function, 'bound_function'):
            raise InvalidFunctionError()
        return self.isSupported(function.bound_function.__name__)


def check_support(f):
    def deco(self, *args, **kwargs):
        if not isinstance(self, SupportBase):
            raise InvalidFunctionError()

        if self.isSupported(f.__name__) or self.force:
            return f(self, *args, **kwargs)
        else:
            raise NotSupportedError()
    deco.bound_function = f
    return deco