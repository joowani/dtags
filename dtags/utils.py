from __future__ import print_function

import errno
import importlib
from sys import stderr

from collections import Mapping, Iterable
try:
    urllib = importlib.import_module('urllib.parse')
except ImportError:
    urllib = importlib.import_module('urllib')
try:
    builtins = importlib.import_module('__builtin__')
except ImportError:
    builtins = importlib.import_module('builtins')


def is_str(obj):
    """Return True iff ``obj`` is a str or unicode

    :param obj: object to check
    :return: True iff ``obj`` is a str or unicode
    """
    base_str = getattr(builtins, 'basestring', None)
    return isinstance(obj, base_str) if base_str else isinstance(obj, str)


def is_list(obj):
    """Check if ``obj`` is an iterable

    :param obj: object to check
    :return: True if ``obj`` is an iterable else False
    """
    return isinstance(obj, Iterable)


def is_dict(obj):
    """Return True iff ``obj`` is a mapping

    :param obj: the object to check
    :return: True if ``obj`` is a mapping else False
    """
    return isinstance(obj, Mapping)


def halt(error_message, exit_code=errno.EPERM):
    """Print ``error_message`` to stderr and exit with ``exit_code``.

    :param error_message: error message
    :param exit_code: linux exit code
    """
    print(error_message, file=stderr)
    exit(exit_code)
