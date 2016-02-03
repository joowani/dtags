#!/usr/bin/env python

import sys
import errno
from argparse import ArgumentParser

from dtags.completion import ChoicesCompleter, autocomplete
from dtags.config import load_tags
from dtags.help import HelpFormatter
from dtags.utils import halt


def main():
    tag_to_paths = load_tags()
    parser = ArgumentParser(
        prog='paths',
        description='dtags - display the directory paths',
        usage='paths tag',
        formatter_class=HelpFormatter,
        add_help=False
    )
    parser.add_argument(
        'tag',
        type=str,
        help='the name of the tag'
    ).completer = ChoicesCompleter(tag_to_paths.keys())
    autocomplete(parser)
    tag = parser.parse_args().tag

    if tag not in tag_to_paths:
        halt('Tag not defined')
        sys.exit(errno.EINVAL)
    for path in tag_to_paths[tag].keys():
        print(path)

if __name__ == '__main__':
    main()
