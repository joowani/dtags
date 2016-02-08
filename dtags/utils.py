"""DTags utility functions."""

import os
import sys
import errno
import shutil


def info(message):
    """Print the message to stdout.

    :param message: info message
    :type message: str
    """
    sys.stdout.write('dtags: {}\n'.format(message))


def halt(message, exit_code=errno.EPERM):
    """Print the message to stderr and exit with the exit code.

    :param message: error message
    :type message: str
    :param exit_code: linux exit code
    :type exit_code: int
    """
    sys.stderr.write('dtags: error: {}\n'.format(message))
    sys.exit(exit_code)


def expand_path(path):
    """Fully expand a directory path.

    :param path: the directory path to expand
    :type path: str
    :return: expanded path
    :rtype: str
    """
    return os.path.realpath(os.path.expanduser(path))


def collapse_path(path):
    """Abbreviate the 'home' portion of the path to '~'.

    :param path: the directory path to shorten
    :returns: the shortened path
    """
    path = expand_path(path)
    home = expand_path('~')
    return path.replace(home, '~') if path.startswith(home) else path


def is_dir(path):
    """Check whether or not the path is a directory.

    :param path: the path to check
    :type path: str
    :returns: True if the path is a directory else False
    :rtype: bool
    """
    return os.path.isdir(expand_path(path))


def is_file(path):
    """Check whether or not the path is a file.

    :param path: the path to check
    :type path: str
    :returns: True if the path is a file else False
    :rtype: bool
    """
    return os.path.isfile(expand_path(path))


def rm_file(path):
    """Remove the file from disk.

    :param path: the path of the file to remove
    :type path: str
    """
    if is_dir(path):
        shutil.rmtree(path, ignore_errors=True)
    elif is_file(path):
        try:
            os.remove(path)
        except OSError as err:
            if err.errno != errno.ENOENT:
                raise err


def msgify(msg):
    """Sanitize the error message.

    Convert the first character of the message to lowercase and remove all
    periods.

    :param msg: the message the sanitize
    :type msg: str
    :returns: the sanitized message
    :rtype: str
    """
    return (msg[0].lower() + msg[1:]).rsplit('.')[0] if msg else ''
