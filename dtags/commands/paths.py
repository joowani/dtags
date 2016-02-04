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
        description='dtags - display the associated directory paths',
        usage='paths <tag>',
        formatter_class=HelpFormatter
    )
    parser.add_argument(
        'tag',
        metavar='<tag>',
        type=str,
        help='the directory tag name'
    ).completer = ChoicesCompleter(tag_to_paths.keys())
    autocomplete(parser)
    tag = parser.parse_args().tag

    paths = list(tag_to_paths.get(tag, {}))
    if not paths:
        halt('Tag not defined')
        sys.exit(errno.EINVAL)

    if len(paths) == 1:
        print(paths[0])
    else:
        selection = [
            '{}: {}'.format(index, path)
            for index, path in enumerate(paths)
        ]
        selection.append('\nSelect directory (0 - {}): '.format(len(paths)))
        try:
            index = input('\n'.join(selection))
        except KeyboardInterrupt:
            sys.exit(1)
        if not index.isdigit():
            halt('Invalid input')
        index = int(index)
        if not (0 <= index < len(paths)):
            halt('Index out of range')
        print(paths[index])


if __name__ == '__main__':
    main()
