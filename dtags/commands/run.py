#!/usr/bin/env python
import os
import subprocess
from collections import OrderedDict
from argparse import ArgumentParser, REMAINDER

from argcomplete import autocomplete

from dtags.colors import MAGENTA, CYAN, END
from dtags.config import load_config
from dtags.completers import ChoicesCompleter
from dtags.formatters import HelpFormatter


def main():
    tags = load_config()['tags']
    parser = ArgumentParser(
        prog="run",
        description="Run commands in one or more directories",
        usage="run [tags] [paths] command",
        add_help=False,
        formatter_class=HelpFormatter
    )
    parser.add_argument(
        "arguments",
        type=str,
        nargs=REMAINDER,
        metavar='[tags] [paths] command',
        help="tags and/or paths followed the command to run"
    ).completer = ChoicesCompleter(tags.keys())
    autocomplete(parser)
    arguments = parser.parse_args().arguments
    if not arguments:
        parser.error("too few arguments")

    index = 0
    paths_and_tags = OrderedDict()
    # Assume what is not a tag/path is the start of the command
    while index < len(arguments):
        arg = arguments[index]
        if arg.startswith('@') and arg in tags:
            for path in sorted(tags[arg]):
                paths_and_tags[path] = arg
            index += 1
        elif os.path.isdir(arg):
            path = os.path.realpath(os.path.expanduser(arg))
            if path not in paths_and_tags:
                paths_and_tags[path] = None
            index += 1
        else:
            break
    command = arguments[index:]
    if not command:
        parser.error("too few arguments")

    for path, tag in paths_and_tags.items():
        print "{start}{path}{end}{tail}".format(
            start=CYAN,
            path=path,
            tail=" ({}{}{}):".format(MAGENTA, tag, END) if tag else ":",
            end=END,
        )
        subprocess.call(command, cwd=path)
        print("")

if __name__ == '__main__':
    main()
