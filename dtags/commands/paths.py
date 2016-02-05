#!/usr/bin/env python

import sys
import argparse

from dtags.config import load_tags


def main():
    parser = argparse.ArgumentParser(
        prog='paths',
        description='dtags - display the directory paths',
        usage='paths <tag>',
    )
    parser.add_argument(
        'tags',
        metavar='[<tag>]',
        nargs=argparse.REMAINDER,
        help='the directory tag name'
    )
    tag_to_paths = load_tags()
    paths = set()
    for tag in parser.parse_args().tags:
        if not tag.startswith('@'):
            tag = '@' + tag
        if tag in tag_to_paths:
            paths.update(tag_to_paths[tag])
    if not paths:
        sys.exit(1)
    print(' '.join(sorted(paths)))

if __name__ == '__main__':
    main()
