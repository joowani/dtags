from __future__ import unicode_literals, print_function

import sys
import atexit
import signal

from dtags import style
from dtags.config import load_mapping, save_mapping
from dtags.utils import close_stdio, finish, expand, abort
from dtags.version import VERSION

USAGE = """Usage:
  u <dir> [<tag>...]
  u --help
  u --version
"""
DESCRIPTION = """
Arguments:
  dir     The directory path
  tag     The directory tag

Untag the target directory. If no tag names are
given, ALL tags mapped to the target directory
are removed."""


def main():
    atexit.register(close_stdio)
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    mapping, excluded = load_mapping()
    args = sys.argv[1:]
    if not args:
        finish(USAGE + DESCRIPTION)
    head, tail = args[0], args[1:]
    if head == '--help':
        finish(USAGE + DESCRIPTION)
    elif head == '--version':
        finish('Version ' + VERSION)
    path = expand(head)
    tags_removed = set()
    for tag in tail if tail else mapping.keys():
        if path in mapping[tag]:
            mapping[tag].remove(path)
            tags_removed.add(tag)
    if not tags_removed:
        finish('Nothing to do')
    save_mapping(mapping)
    if excluded:
        print('Cleaned the following invalid entries:\n' + excluded + '\n')
    finish(style.path(path) + ' ' + ' '.join(
        style.sign('-') + style.tag(tag) for tag in sorted(tags_removed)
    ))
