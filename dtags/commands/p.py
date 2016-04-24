from __future__ import unicode_literals, print_function

import os
import sys
import atexit
import signal
import tempfile
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
  p [-i] <targets> <command> [<arg>...]
  p --help
  p --version
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

Execute commands in one or more directories in parallel.
Multiple targets can be given by separating them with
commas and without whitespaces."""


def _send_sigterm(child_process):
    """Send SIGTERM to the specified child process."""
    try:
        os.killpg(os.getpgid(child_process.pid), signal.SIGKILL)
    except OSError as kill_error:
        # If the process is already dead, nothing needs to be done
        if kill_error.errno != 3:  # ESRCH
            raise kill_error


def _cleanup_resources():
    """Kill all child processes and close any open files."""
    global temp_file, process, processes

    if temp_file is not None:
        temp_file.close()
    if process is not None:
        _send_sigterm(process)
    for _, _, child_process, open_file in processes:
        _send_sigterm(child_process)
        if open_file is not None:
            open_file.close()
    close_stdio()


def _handle_signal(signum, *_):
    """Send SIGTERM to all child processes."""
    _cleanup_resources()
    sys.exit(127 + signum)


def main():
    global temp_file, process, processes

    atexit.register(_cleanup_resources)
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
        abort(USAGE + 'p: missing argument: ' + style.bad('<targets>'))
    elif head == '-i' and tail:
        interactive = True
        head, tail = tail[0], tail[1:]
    elif head.startswith('-'):
        abort(USAGE + 'p: invalid argument: ' + style.bad(head))

    # Parse the positional arguments
    if not tail:
        abort(USAGE + 'p: missing argument: ' + style.bad('<command>'))
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
                abort(USAGE + 'p: invalid target: ' + style.bad(target))

    # Check which shell is in use (e.g. zsh, bash, fish)
    shell = os.environ.get('SHELL')
    if shell is None:
        abort('p: undefined environment variable: ' + style.bad('SHELL'))

    if interactive:
        cmd = [shell, '-i', '-c', sp.list2cmdline(tail)]
    else:
        cmd = [shell, '-c', sp.list2cmdline(tail)]

    # Add signal handlers to terminate child processes gracefully
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGABRT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    # Execute in parallel and pipe the output to temporary files
    for directory in sorted(directories):
        tags = directories[directory]
        temp_file = tempfile.TemporaryFile(mode='w+t')
        process = sp.Popen(
            cmd,
            cwd=directory,
            stdout=temp_file,
            stderr=temp_file,
            preexec_fn=os.setsid
        )
        processes.append((directory, tags, process, temp_file))

    # Read from the temporary files back to stdout line by line
    sys.stdout.write('\n')
    for directory, tags, process, temp_file in processes:
        status = process.wait()
        tags = [style.tag(tag) for tag in tags if tag]
        sys.stdout.write('{} {}{}\n'.format(
            style.msg('in'), style.path(directory),
            ((' ' + ' '.join(tags)) if tags else '') + style.msg(':')
        ))
        temp_file.seek(0)
        for line in temp_file:
            sys.stdout.write(line)
        temp_file.close()
        if status != 0:
            sys.stdout.write(style.bad('Exit status: {}\n\n'.format(status)))
        else:
            sys.stdout.write('\n\n')
