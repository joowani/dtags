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

from dtags.colors import RED, PINK, CYAN, YELLOW, CLEAR
from dtags.completion import ChoicesCompleter, autocomplete
from dtags.config import load_tags
from dtags.help import HelpFormatter
from dtags.utils import expand_path

shell = os.getenv('SHELL')
tmp_file = None
current_process = None
child_processes = []
cmd_description = """
dtags - run commands in directories

e.g. the command {y}run @a @b ~/foo ~/bar ls -la{x}:

    runs {y}ls -la{x} in all directories with tag {p}@a{x}
    runs {y}ls -la{x} in all directories with tag {p}@b{x}
    runs {y}ls -la{x} in directory {c}~/foo{x}
    runs {y}ls -la{x} in directory {c}~/bar{x}

""".format(p=PINK, c=CYAN, y=YELLOW, x=CLEAR)


def contains_ctrl_error_msg(line):
    """Helper function for filtering out bash ioctl error messages."""
    if 'no job control in this shell' in line:
        return True
    if 'Inappropriate ioctl for device' in line:
        return True


def send_sigterm(child_process):
    """Send sigterm to the target child process."""
    try:
        os.killpg(os.getpgid(child_process.pid), signal.SIGKILL)
    except OSError as err:
        if err.errno != errno.ESRCH:
            raise
        # If the process is already killed for some reason, do nothing


def kill_signal_handler(signum, frame):
    """Clean up resources when sigterm or sigint is received."""
    cleanup_resources()
    sys.exit(127 + signum)


def cleanup_resources():
    """Kill child processes and remove temporary files."""
    global tmp_file, current_process, child_processes
    if tmp_file is not None:
        tmp_file.close()
    if current_process is not None:
        send_sigterm(current_process)
    for _, _, proc, tmp in child_processes:
        send_sigterm(proc)
        tmp.close()


def main():
    global tmp_file, current_process, child_processes

    # https://stackoverflow.com/questions/25099895/
    signal.signal(signal.SIGTTOU, signal.SIG_IGN)

    # Ensure that child processes are cleaned up
    signal.signal(signal.SIGINT, kill_signal_handler)
    signal.signal(signal.SIGTERM, kill_signal_handler)
    atexit.register(cleanup_resources)

    tag_to_paths = load_tags()
    parser = argparse.ArgumentParser(
        prog='run',
        description=cmd_description,
        usage='run [options] [targets] command',
        formatter_class=HelpFormatter
    )
    parser.add_argument(
        '-p', '--parallel',
        help='run the command in parallel',
        action='store_true'
    )
    parser.add_argument(
        '-e', '--exit-codes',
        help='display the exit codes',
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

    # Join the command arguments into a string
    command_arguments = parsed.arguments[index:]
    if len(command_arguments) == 0:
        command = None
    elif len(command_arguments) == 1:
        command = ' '.join(command_arguments)
    else:
        command = ' '.join(
            "'{}'".format(arg) if ' ' in arg else arg
            for arg in command_arguments
        )
    if not (targets and command):
        parser.error('too few arguments')

    if parsed.parallel:
        # Run the command in parallel
        for path, tag in targets.items():
            tmp_file = tempfile.TemporaryFile(mode='w+t')
            current_process = subprocess.Popen(
                '{} -i -c "{}"'.format(shell, command),
                cwd=path,
                shell=True,
                stdout=tmp_file,
                stderr=tmp_file,
                preexec_fn=os.setsid,
            )
            child_processes.append((path, tag, current_process, tmp_file))
        for path, tag, current_process, tmp_file in child_processes:
            exit_code = current_process.wait()
            tail = ' ({}{}{})'.format(PINK, tag, CLEAR) if tag else ':'
            print('{}>>> {}{}{}{}'.format(
                YELLOW, CYAN, path, tail, CLEAR
            ))
            tmp_file.seek(0)
            lines = tmp_file.readlines()
            offset = 0
            if len(lines) > 0 and contains_ctrl_error_msg(lines[0]):
                offset += 1
            if len(lines) > 1 and contains_ctrl_error_msg(lines[1]):
                offset += 1
            sys.stdout.write(''.join(lines[offset:]))
            tmp_file.close()
            if parsed.exit_codes:
                print('{}>>> {}exit code: {}{}'.format(
                    YELLOW, RED, exit_code, CLEAR
                ))
            sys.stdout.write('\n')
    else:
        # Run the command sequentially
        full_command = []
        for path, tag in targets.items():
            tag_info = ' ({}{}{})'.format(PINK, tag, CLEAR) if tag else ':'
            if parsed.exit_codes:
                tail = 'printf "{}>>> {}exit code: $?{}\n\n"'.format(
                    YELLOW, RED, CLEAR
                )
            else:
                tail = 'printf "\n"'
            full_command.append(
                '(printf "{header}"; cd {path} && {cmd};{tail})'.format(
                    header='{}>>> {}{}{}{}\n'.format(
                        YELLOW, CYAN, path, CLEAR, tag_info
                    ),
                    path=path,
                    cmd=command,
                    tail=tail
                )
            )
        subprocess.call(
            [shell, '-i', '-c', '{}'.format(';'.join(full_command))],
            stderr=sys.stdout.fileno()
        )
        # https://stackoverflow.com/questions/25099895/
        os.tcsetpgrp(0, os.getpgrp())
    sys.exit(0)
