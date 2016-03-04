from __future__ import unicode_literals

import sys

TTY = sys.stdout.isatty()

# Normal color
BLACK = '\033[38;5;240m'
BLUE = '\033[38;5;27m'
BROWN = '\033[38;5;88m'
GRAY = '\033[38;5;249m'
GREEN = '\033[38;5;154m'
ORANGE = '\033[38;5;208m'
PURPLE = '\033[38;5;141m'
RED = '\033[38;5;009m'
SKY = '\033[38;5;39m'
TURQUOISE = '\033[38;5;37m'
YELLOW = '\033[38;5;214m'

# Bold
BLACK_BOLD = '\033[1;38;5;240m'
BLUE_BOLD = '\033[1;38;5;27m'
BROWN_BOLD = '\033[1;38;5;88m'
GRAY_BOLD = '\033[1;38;5;249m'
GREEN_BOLD = '\033[1;38;5;154m'
ORANGE_BOLD = '\033[1;38;5;208m'
PURPLE_BOLD = '\033[1;38;5;141m'
RED_BOLD = '\033[1;38;5;009m'
SKY_BOLD = '\033[1;38;5;39m'
TURQUOISE_BOLD = '\033[1;38;5;37m'
YELLOW_BOLD = '\033[1;38;5;214m'

# Clear format
CLEAR = '\033[0m'


def tag(value, highlight=False, tty=TTY):
    """Style the directory tag name.

    :param value: the directory tag name to style
    :param highlight: True iff the tag is to be highlighted
    :param tty: True iff the output is going to a terminal
    :return: the styled directory tag name
    """
    if tty:
        if highlight:
            return BLACK + '#' + GREEN_BOLD + value + CLEAR
        else:
            return BLACK + '#' + GRAY + value + CLEAR
    return '#' + value


def path(value, highlight=False, tty=TTY):
    """Style the directory path.

    :param value: the directory path to style
    :param highlight: True iff the path is to be highlighted
    :param tty: True iff the output is going to a terminal
    :return: the styled directory path
    """
    if tty:
        if highlight:
            return GREEN_BOLD + value + CLEAR
        else:
            return SKY + value + CLEAR
    return value


def bad_chars(value, tty=TTY):
    """Style the set of invalid characters in directory tags/paths.

    :param value: the set of invalid characters to style
    :param tty: True iff the output is going to a terminal
    :return: the styled invalid characters
    """
    if tty:
        return ' '.join("{}{}{}".format(RED, c, CLEAR) for c in value)
    return ' '.join("{}".format(c) for c in value)


def cmd(value, tty=TTY):
    """Style the linux command string.

    :param value: the linux command string to style
    :param tty: True iff the output is going to a terminal
    :return: the styled command
    """
    return '{}{}{}'.format(GREEN, value, CLEAR) if tty else value


def bad(value, tty=TTY):
    """Style the invalid entry (e.g. directory path, tag, argument).

    :param value: the invalid value to style
    :param tty: True iff the output is going to a terminal
    :return: the styled value
    """
    return '{}{}{}'.format(RED, value, CLEAR) if tty else value


def msg(value, tty=TTY):
    """Style the message.

    :param value: the message to style
    :param tty: True iff the output is going to a terminal
    :return: the styled message
    """
    return '{}{}{}'.format(BLACK, value, CLEAR) if tty else value


def sign(value, tty=TTY):
    """Style the sign (e.g '+' and '-' symbols).

    :param value: the sign to style
    :param tty: True iff the output is going to a terminal
    :return: the styled sign
    """
    return '{}{}{}'.format(ORANGE_BOLD, value, CLEAR) if tty else value
