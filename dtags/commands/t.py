from __future__ import unicode_literals, print_function

import os
import sys
import atexit
import signal

from dtags import style
from dtags.chars import get_invalid_path_chars, get_invalid_tag_chars
from dtags.config import load_mapping, save_mapping
from dtags.utils import close_stdio, abort, finish, expand
from dtags.version import VERSION

USAGE = """Usage:
  t <dir> [<tag>...]
  t --help
  t --version
"""
DESCRIPTION = """
Arguments:
  dir     The directory path
  tag     The directory tag

Tag the target directory. If no tag names are given,
the basename of the directory path is used instead."""


def main():
    atexit.register(close_stdio)
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    args = sys.argv[1:]
    if not args:
        finish(USAGE + DESCRIPTION)
    head, tail = args[0], args[1:]
    if head == '--help':
        finish(USAGE + DESCRIPTION)
    elif head == '--version':
        finish('Version ' + VERSION)
    path = expand(head)
    invalid_path_chars = get_invalid_path_chars(path)
    if invalid_path_chars:
        abort('t: directory path {} contains bad characters {}'.format(
            style.bad(path), style.bad_chars(invalid_path_chars)
        ))
    if not os.path.isdir(path):
        abort('t: invalid directory: ' + style.bad(path))
    mapping, excluded = load_mapping()
    tags_added = set()
    if not tail:
        tail.append(os.path.basename(path))
    for tag in tail:
        if not tag[0].isalpha():
            abort('t: tag name {} does not start with an alphabet'
                  .format(style.bad(tag)))
        if ' ' in tag:
            abort('t: tag name {} contains whitespaces'.format(style.bad(tag)))
        invalid_tag_chars = get_invalid_tag_chars(tag)
        if invalid_tag_chars:
            abort('t: tag name {} contains bad characters {}'.format(
                style.bad(tag), style.bad_chars(invalid_tag_chars)
            ))
        if path not in mapping[tag]:
            mapping[tag].add(path)
            tags_added.add(tag)
    if tags_added or excluded:
        save_mapping(mapping)
    if excluded:
        print('Cleaned the following invalid entries:\n' + excluded + '\n')
    if not tags_added:
        finish('Nothing to do')
    else:
        finish(style.path(path) + ' ' + ' '.join(
            style.sign('+') + style.tag(tag) for tag in sorted(tags_added)
        ))
