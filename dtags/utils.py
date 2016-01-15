from __future__ import print_function

import os
import sys
import errno
import importlib
from sys import stderr

from collections import Mapping
# Importing this way for python 2 and 3 compatibility
try:
    urllib = importlib.import_module('urllib.parse')
except ImportError:
    urllib = importlib.import_module('urllib')
try:
    builtins = importlib.import_module('__builtin__')
except ImportError:
    builtins = importlib.import_module('builtins')


def is_str(obj):
    """Check if the object is a str or a unicode

    :param obj: object to check
    :return: True if str or unicode, else False
    """
    base_str = getattr(builtins, 'basestring', None)
    return isinstance(obj, base_str) if base_str else isinstance(obj, str)


def is_list(obj):
    """Check if the object is an iterable

    :param obj: object to check
    :return: True if iterable, else False
    """
    return type(obj) == list


def is_dict(obj):
    """Check if the object is a mapping

    :param obj: object to check
    :return: True if mapping, else False
    """
    return isinstance(obj, Mapping)


def halt(message, exit_code=errno.EPERM):
    """Print the message to stderr and exit with the exit code.

    :param message: error message
    :param exit_code: linux exit code
    """
    print(message, file=stderr)
    sys.exit(exit_code)


def expand_path(path):
    """Fully expand a directory path.

    :param path: a valid directory path
    :return: expanded path
    """
    return os.path.realpath(os.path.expanduser(path))


def shrink_path(path):
    """Shrink the 'home' portion of the path to '~'.

    :param path: a valid directory path
    :return: shortened path
    """
    path = expand_path(path)
    home = expand_path('~')
    return path.replace(home, '~') if path.startswith(home) else path


def msgify(exception):
    """Format the exception message.

    1. Convert any capital characters to lowercase
    2. Strip any periods or newlines

    :param exception: the exception whose message to msgify
    :return: msgified string
    """
    string = str(exception)
    string = string if len(string) == 0 else string[0].lower() + string[1:]
    return string.strip('.')


def safe_remove(path):
    """Remove a file safely.

    If the file does not exist, then do nothing.

    :param path: path of the file to remove
    """
    try:
        os.remove(path)
    except OSError:
        pass
