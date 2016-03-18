from __future__ import unicode_literals

from dtags import style

USAGE = """Usage:
  d [<dir>|<tag>]
  d --help
  d --version
"""
DESCRIPTION = """
Arguments:
  dir         The directory path
  tag         The directory tag

Options:
  --help      Display the help menu
  --version   Display the version

Change directory. If the destination is not
specified it defaults to the home directory.
If multiple directories are associated with
the same tag, a selection menu is displayed.
"""

ARG_ERR = '%sInvalid argument: %s\n'
CHOICE = '%s: %s\n'
DEST_ERR = '%sInvalid destination: %s\n'
GOTO_MSG = 'Going to %s\n'
INDEX_ERR = 'Index out of range: %s\n'
INPUT_ERR = 'Invalid input: %s\n'
PROMPT = '\nSelect directory (1 - %s): '

# Style the messages if the output is going to a terminal
tty = True
ARG_ERR_TTY = '%sInvalid argument: ' + style.bad('%s\n', tty=tty)
CHOICE_TTY = style.msg('%s: ', tty=tty) + style.path('%s\n', tty=tty)
DEST_ERR_TTY = '%sInvalid destination: ' + style.bad('%s\n', tty=tty)
GOTO_MSG_TTY = style.msg('Going to ', tty=tty) + style.path('%s\n', tty=tty)
INDEX_ERR_TTY = 'Index out of range: ' + style.bad('%s\n', tty=tty)
INPUT_ERR_TTY = 'Invalid input: ' + style.bad('%s\n', tty=tty)
PROMPT_TTY = style.msg('\nSelect directory (1 - %s): ', tty=tty)
