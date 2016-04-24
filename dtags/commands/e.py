from __future__ import unicode_literals, print_function

import os
import sys
import atexit
import signal
import collections
import subprocess as sp

from dtags import style
from dtags.config import load_mapping
from dtags.utils import close_stdio, abort, finish, expand
from dtags.version import VERSION

temp_file = None
process = None
processes = []

USAGE = """Usage:
  e [-i] <targets> <command> [<arg>...]
  e --help
  e --version
"""
DESCRIPTION = """
Arguments:
  targets     Comma separated directory tags or paths
  command     The command to execute
  arg         The command arguments

Options:
  -i          Execute the commands via interactive shell
  --help      Display the help menu
  --version   Display the version

Execute commands in one or more directories.
Multiple targets can be given by separating
them with commas and without whitespaces."""


def main():
    atexit.register(close_stdio)
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    mapping, excluded = load_mapping()
    if excluded:
        print(
            'Found invalid entries in the mapping:\n' +
            excluded + '\nRun ' + style.cmd('dtags clean') +
            ' to remove them' + '\n'
        )
    # Parse the optional arguments
    interactive = False
    args = sys.argv[1:]
    if not args:
        finish(USAGE + DESCRIPTION)
    head, tail = args[0], args[1:]
    if head == '--help':
        finish(USAGE + DESCRIPTION)
    elif head == '--version':
        finish('Version ' + VERSION)
    elif head == '-i' and not tail:
        abort(USAGE + 'e: missing argument: ' + style.bad('<targets>'))
    elif head == '-i' and tail:
        interactive = True
        head, tail = tail[0], tail[1:]
    elif head.startswith('-'):
        abort(USAGE + 'e: invalid argument: ' + style.bad(head))

    # Parse the positional arguments
    if not tail:
        abort(USAGE + 'e: missing argument: ' + style.bad('<command>'))
    directories = collections.defaultdict(set)
    for target in head.split(','):
        if not target:
            continue
        elif target in mapping:
            for directory in sorted(mapping[target]):
                directories[directory].add(target)
        else:
            path = expand(target)
            if os.path.isdir(path):
                directories[path].add(None)
            else:
                abort(USAGE + 'e: invalid target: ' + style.bad(target))
    cmd = sp.list2cmdline(tail)

    # Check which shell is in use (e.g. zsh, bash, fish)
    shell = os.environ.get('SHELL')
    if shell is None:
        abort('e: undefined environment variable: ' + style.bad('SHELL'))

    # Generate the command string and execute all in one subprocess call
    cmds = []
    if 'fish' in shell:
        status_printf = (
            'if [ $status = 0 ]; printf "\n\n"; else; printf "{}\n\n"; end'
            .format(style.bad('Exit status: $status'))
        )
    else:
        status_printf = (
            'if [ $? -eq 0 ]; then printf "\n\n"; else printf "{}\n\n"; fi'
            .format(style.bad('Exit status: $?'))
        )
    for directory in sorted(directories):
        tags = [style.tag(tag) for tag in directories[directory] if tag]
        cmds.append('printf "{} {}{}\n"; cd "{}"; {}; {}'.format(
            style.msg('in'), style.path(directory),
            ((' ' + ' '.join(tags)) if tags else '') + style.msg(':'),
            directory, cmd, status_printf
        ))
    sys.stdout.write('\n')
    sys.stdout.flush()  # flush for printing chronologically
    if interactive:
        sp.call([shell, '-i', '-c', ';'.join(cmds)], stderr=sp.STDOUT)
    else:
        sp.call([shell, '-c', ';'.join(cmds)], stderr=sp.STDOUT)
