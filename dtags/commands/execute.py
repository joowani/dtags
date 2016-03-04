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
  e [-p] <targets> <command> [<arg>...]
  e --help
  e --version
"""
DESCRIPTION = """
Arguments:
  targets     Comma separated directory tags or paths
  command     The command to execute
  arg         The command arguments

Options:
  -p          Execute the commands in parallel
  --help      Display the help menu
  --version   Display the version

Execute commands in one or more directories.
Multiple targets can be given by separating
them with commas and without whitespaces."""


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
    parallel = False
    args = sys.argv[1:]
    if not args:
        finish(USAGE + DESCRIPTION)
    head, tail = args[0], args[1:]
    if head == '--help':
        finish(USAGE + DESCRIPTION)
    elif head == '--version':
        finish('Version ' + VERSION)
    elif head == '-p' and not tail:
        abort(USAGE + 'Missing argument: ' + style.bad('<targets>'))
    elif head == '-p' and tail:
        parallel = True
        head, tail = tail[0], tail[1:]
    elif head.startswith('-'):
        abort(USAGE + 'Invalid argument: ' + style.bad(head))

    # Parse the positional arguments
    if not tail:
        abort(USAGE + 'Missing argument: ' + style.bad('<command>'))
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
                abort(USAGE + 'Invalid target: ' + style.bad(target))
    command = sp.list2cmdline(tail)

    # Check which shell is in use (e.g. zsh, bash, fish)
    shell = os.environ.get('SHELL')
    if shell is None:
        abort('Undefined environment variable: ' + style.bad('SHELL'))

    # Execute the command in the targeted directories
    msg_head = style.msg('Executing command ') + style.cmd(command)
    if parallel:
        global temp_file, process, processes

        # Add signal handlers to terminate child processes gracefully
        signal.signal(signal.SIGINT, _handle_signal)
        signal.signal(signal.SIGABRT, _handle_signal)
        signal.signal(signal.SIGTERM, _handle_signal)

        # Execute in parallel and pipe the output to temporary files
        sys.stdout.write(msg_head + style.msg(' in parallel...\n\n'))
        for directory in sorted(directories):
            tags = directories[directory]
            temp_file = tempfile.TemporaryFile(mode='w+t')
            process = sp.Popen(
                [shell, '-i', '-c', command],
                cwd=directory,
                stdout=temp_file,
                stderr=temp_file,
                preexec_fn=os.setsid
            )
            processes.append((directory, tags, process, temp_file))

        # Read from the temporary files back to stdout line by line
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
            sys.stdout.write(style.msg('Exit status: {}\n\n'.format(status)))
    else:
        # Generate the command string and execute all in one subprocess call
        commands = []
        status_printf = 'printf "{}\n\n"'.format(style.msg(
            'Exit status: ' + ('$status' if '/fish' in shell else '$?')
        ))
        for directory in sorted(directories):
            tags = [style.tag(tag) for tag in directories[directory] if tag]
            commands.append('printf "{} {}{}\n"; cd "{}"; {};{}'.format(
                style.msg('in'), style.path(directory),
                ((' ' + ' '.join(tags)) if tags else '') + style.msg(':'),
                directory, command, status_printf
            ))
        sys.stdout.write(msg_head + style.msg(' in sequence...\n\n'))
        sys.stdout.flush()  # flush for printing chronologically
        sp.call([shell, '-i', '-c', ';'.join(commands)], stderr=sp.STDOUT)
