from __future__ import unicode_literals

import os
import sys


def finish(message):
    """Write the message to stdout and exit with 0.

    :param message: the message to write
    """
    sys.stdout.write(message + '\n')
    sys.exit(0)


def warn(message):
    """Write the warning message to stderr.

    :param message: the warning message to write
    """
    sys.stderr.write(message + '\n')


def abort(message, exit_code=1):
    """Write the message to stderr and exit with the given exit code.

    :param message: the error message to write
    :param exit_code: the exit code
    """
    sys.stderr.write(message + '\n')
    sys.exit(exit_code)


def expand(path):
    """Fully expand the given file path.

    :param path: the file path to expand
    :return: the expanded path
    """
    return os.path.abspath(os.path.expanduser(path))


def close_stdio():
    """Close stdout and stderr."""
    try:
        sys.stdout.close()
    except IOError:
        pass
    try:
        sys.stderr.close()
    except IOError:
        pass


def rm_files(*filenames):
    """Remove the files from disk while ignoring ENOENT.

    :param filenames: the files to remove
    """
    for filename in filenames:
        try:
            os.remove(filename)
        except OSError as remove_error:
            if remove_error.errno != 2:  # ENOENT
                raise remove_error
