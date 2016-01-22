#!/usr/bin/env python

import os
import sys
import errno
import signal
import atexit
import argparse
import tempfile
import subprocess
from collections import OrderedDict

from dtags.colors import *
from dtags.completion import ChoicesCompleter, autocomplete
from dtags.config import load_tags
from dtags.help import HelpFormatter
from dtags.utils import expand_path

tmp_file = None
process = None
processes = []
cmd_description = """
dtags - run commands in directories

e.g. the command {y}run @a @b ~/foo ~/bar ls -la{x}:

    runs {y}ls -la{x} in all directories with tag {p}@a{x}
    runs {y}ls -la{x} in all directories with tag {p}@b{x}
    runs {y}ls -la{x} in directory {c}~/foo{x}
    runs {y}ls -la{x} in directory {c}~/bar{x}

""".format(p=PINK, c=CYAN, y=YELLOW, x=CLEAR)


def _print_header(tag, path):
    """Print the run information header."""
    tail = ' ({}{}{}):'.format(PINK, tag, CLEAR) if tag else ':'
    print('{}{}{}{}'.format(CYAN, path, tail, CLEAR))


def _print_error(cmd, err):
    """Print the error message."""
    print('Failed to run {}{}{}: {}'.format(YELLOW, cmd, CLEAR, err))


def _print_exit_code(exit_code):
    """Print the exit code from process."""
    print('{}Exit Code: {}{}'.format(RED, exit_code, CLEAR))


def _send_sigterm(target_process):
    """Send sigterm to the target child process."""
    try:
        os.killpg(os.getpgid(target_process.pid), signal.SIGKILL)
    except OSError as err:
        # If the process is already killed for some reason, do nothing
        if err.errno != errno.ESRCH:
            raise


def _cleanup_resources():
    """Kill child processes and remove temporary files."""
    global tmp_file, process, processes
    if tmp_file is not None:
        tmp_file.close()
    if process is not None:
        _send_sigterm(process)
    for _, _, proc, tmp in processes:
        _send_sigterm(proc)
        tmp.close()


def _kill_signal_handler(signum, frame):
    """Clean up resources when sigterm or sigint is received."""
    _cleanup_resources()
    sys.exit(127 + signum)


def main():
    global tmp_file, process, processes

    # Ensure that child processes are cleaned up
    signal.signal(signal.SIGINT, _kill_signal_handler)
    signal.signal(signal.SIGTERM, _kill_signal_handler)
    atexit.register(_cleanup_resources)

    tag_to_paths = load_tags()
    parser = argparse.ArgumentParser(
        prog='run',
        description=cmd_description,
        usage='run [options] [targets] command',
        formatter_class=HelpFormatter
    )
    parser.add_argument(
        '-p', '--parallel',
        help='run the commands in parallel',
        action='store_true'
    )
    parser.add_argument(
        '-e', '--exit-codes',
        help='display exit codes',
        action='store_true'
    )
    parser.add_argument(
        'arguments',
        type=str,
        nargs=argparse.REMAINDER,
        metavar='[targets]',
        help='tags or paths to run the command for'
    ).completer = ChoicesCompleter(tag_to_paths.keys())
    autocomplete(parser)
    parsed = parser.parse_args()

    # Separate the targets from the command
    index = 0
    targets = OrderedDict()
    while index < len(parsed.arguments):
        target = parsed.arguments[index]
        if target in tag_to_paths:
            for path in sorted(tag_to_paths[target].keys()):
                targets[path] = target
            index += 1
        elif target.startswith('@'):
            parser.error('unknown tag {}'.format(target))
        elif os.path.isdir(target):
            path = expand_path(target)
            if path not in targets:
                targets[path] = None
            index += 1
        else:
            break  # beginning of the command
    command = ' '.join(
        "'{}'".format(arg) if ' ' in arg else arg
        for arg in parsed.arguments[index:]
    )
    if not (targets and command):
        parser.error('too few arguments')

    exit_code = 0
    if parsed.parallel:
        # Run the command in parallel
        for path, tag in targets.items():
            tmp_file = tempfile.TemporaryFile(mode='w+t')
            process = subprocess.Popen(
                command,
                cwd=path,
                stdout=tmp_file,
                stderr=tmp_file,
                shell=True,
                preexec_fn=os.setsid
            )
            processes.append((path, tag, process, tmp_file))
        for path, tag, process, tmp_file in processes:
            child_exit_code = process.wait()
            tmp_file.seek(0)
            _print_header(tag, path)
            sys.stdout.write(tmp_file.read())
            tmp_file.close()
            if child_exit_code != 0:
                exit_code = 1
            if parsed.exit_codes:
                _print_exit_code(child_exit_code)
            sys.stdout.write('\n')
    else:
        # Run the command sequentially
        for path, tag in targets.items():
            _print_header(tag, path)
            child_exit_code = subprocess.call(
                command,
                cwd=path,
                shell=True,
                stderr=sys.stdout.fileno()
            )
            if child_exit_code != 0:
                exit_code = 1
            if parsed.exit_codes:
                _print_exit_code(child_exit_code)
            sys.stdout.write('\n')
    sys.exit(exit_code)
