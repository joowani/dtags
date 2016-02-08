import os
import sys
import errno
import signal
import atexit
import argparse
import tempfile
import subprocess
from collections import OrderedDict

from dtags import SHELL
from dtags.colors import RED, PINK, CYAN, YELLOW, END
from dtags.config import load_mapping
from dtags.help import HelpFormatter
from dtags.utils import expand_path, collapse_path, is_dir

temp_file = None
process = None
processes = []

cmd_description = """
dtags - run commands in directories

e.g. {y}run @a @b ~/foo ~/bar ls{x} runs {y}ls{x} in:

    all directories with tag {p}@a{x}
    all directories with tag {p}@b{x}
    directory {c}~/foo{x}
    directory {c}~/bar{x}

""".format(p=PINK, c=CYAN, y=YELLOW, x=END)


def send_sigterm(child_process):
    """Send sigterm to the target child process.

    :param child_process: the child process to kill
    :type child_process: subprocess.Popen
    """
    try:
        os.killpg(os.getpgid(child_process.pid), signal.SIGKILL)
    except OSError as kill_error:
        # If the process is already dead, do nothing
        if kill_error.errno != errno.ESRCH:
            raise kill_error


def cleanup_resources():
    """Kill child processes and remove temporary files."""
    global temp_file, process, processes
    if temp_file is not None:
        temp_file.close()
    if process is not None:
        send_sigterm(process)
    for _, _, process, temp_file in processes:
        send_sigterm(process)
        temp_file.close()


def handle_signal(signum, *_):
    """Send sigterm to child processes on sigint/sigterm.

    :param signum: signal number
    :type signum: int
    """
    cleanup_resources()
    sys.exit(127 + signum)


def main():
    global temp_file, process, processes
    parser = argparse.ArgumentParser(
        prog='dtags: run',
        description=cmd_description,
        usage='run [option] [target] command',
        formatter_class=HelpFormatter
    )
    parser.add_argument(
        '-i', '--interactive',
        help='run the command via interactive shell',
        action='store_true'
    )
    parser.add_argument(
        '-p', '--parallel',
        help='run the command in parallel',
        action='store_true'
    )
    parser.add_argument(
        '-e', '--exit-codes',
        help='show the exit codes for each run',
        action='store_true'
    )
    parser.add_argument(
        'arguments',
        type=str,
        nargs=argparse.REMAINDER,
        metavar='target',
        help='directory path or tag name'
    )
    args = parser.parse_args()
    mapping = load_mapping()

    # Ensure that child processes are cleaned up
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    atexit.register(cleanup_resources)

    # Split the targets from the command
    index = 0
    targets = OrderedDict()
    while index < len(args.arguments):
        target = args.arguments[index]
        if target in mapping:
            for path in sorted(mapping[target]):
                if is_dir(path):
                    targets[expand_path(path)] = target
            index += 1
        elif target.startswith('@'):
            parser.error('unknown tag {}'.format(target))
        elif is_dir(target):
            if collapse_path(target) not in targets:
                targets[expand_path(target)] = None
            index += 1
        else:
            # the command arguments start here
            break
    command_args = args.arguments[index:]
    if not (targets and command_args):
        parser.error('too few arguments')
    elif len(command_args) > 1 and ' ' in command_args[0]:
        parser.error('whitespace in first command argument')
    command = ' '.join([
        '"{}"'.format(cmd_arg) if ' ' in cmd_arg else cmd_arg
        for cmd_arg in command_args
    ] if len(command_args) > 1 else command_args)
    if args.parallel:
        for path, tag in targets.items():
            temp_file = tempfile.TemporaryFile(mode='w+t')
            if args.interactive:
                process = subprocess.Popen(
                    [SHELL, '-i', '-c', command],
                    cwd=path,
                    stdout=temp_file,
                    stderr=temp_file,
                    preexec_fn=os.setsid
                )
            else:
                process = subprocess.Popen(
                    command,
                    cwd=path,
                    shell=True,
                    stdout=temp_file,
                    stderr=temp_file,
                    preexec_fn=os.setsid
                )
            processes.append((path, tag, process, temp_file))
        for path, tag, process, temp_file in processes:
            exit_code = process.wait()
            tail = ' {}{}{}'.format(PINK, tag, END) if tag else ''
            print('{}>>> {}{}{}{}'.format(YELLOW, CYAN, path, END, tail))
            temp_file.seek(0)
            sys.stdout.write(temp_file.read())
            temp_file.close()
            sys.stdout.write('{}>>> {}exit code: {}{}\n\n'.format(
                YELLOW, RED, exit_code, END
            ) if args.exit_codes else '\n')
    else:
        full_command = []
        exit_code_string = 'printf "{}>>> {}exit code: $?{}\n\n"'.format(
            YELLOW, RED, END
        ) if args.exit_codes else 'printf "\n"'
        for path, tag in targets.items():
            tag_name = ' {}{}{}'.format(PINK, tag, END) if tag else ''
            full_command.append('(printf "{}"; cd {} && {};{})'.format(
                '{}>>> {}{}{}{}\n'.format(YELLOW, CYAN, path, END, tag_name),
                path, command, exit_code_string
            ))
        if args.interactive:
            subprocess.call(
                [SHELL, '-i', '-c', ';'.join(full_command)],
                stderr=sys.stdout.fileno(),
            )
        else:
            subprocess.call(
                ';'.join(full_command),
                stderr=sys.stdout.fileno(),
                shell=True
            )
