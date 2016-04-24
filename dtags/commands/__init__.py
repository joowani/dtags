from __future__ import unicode_literals, print_function

import os
import io
import sys
import shlex
import atexit
import signal
import subprocess as sp
from collections import defaultdict
from tempfile import NamedTemporaryFile as TempFile

from dtags import style, CFG_DIR, MAPPING_FILE, TAGS_FILE
from dtags.commands import d
from dtags.chars import get_invalid_tag_chars
from dtags.config import load_mapping, save_mapping, parse_mapping
from dtags.shells import SUPPORTED_SHELLS
from dtags.utils import close_stdio, abort, finish, expand, rm_files
from dtags.version import VERSION

USAGE = """Usage:
  dtags list [<dir>|<tag>...]
  dtags reverse [<dir>|<tag>...]
  dtags edit
  dtags clean
  dtags commands
  dtags --help
  dtags --version
"""
DESCRIPTION = """
Commands:
  list       Display directories-to-tags mapping
  reverse    Display tags-to-directories mapping
  edit       Edit tags and directories via editor
  clean      Remove invalid tags and directories
  commands   List all available dtags commands

Arguments:
  dir        The directory path
  tag        The directory tag

Options:
  --help     Display the help menu
  --version  Display the version"""

EDIT_HELP_COMMENTS = """# Format: <dir>,<tag>,<tag>,<tag>...
# <dir>: the directory path
# <tag>: the directory tag
#
# Examples:
# /home/user/app/backend/mysql,app,backend,mysql
# /home/user/app/backend/redis,app,backend,redis
# /home/user/app/frontend/web,app,frontend,web
"""

COMMANDS = """t: tag a specified directory
u: untag a specified directory
d: go to the specified directory
e: execute command in directories
p: execute command in parallel
"""


def _edit(args):
    """Edit the mapping directly using an editor."""
    if args:
        abort(USAGE + 'dtags: too many arguments')
    try:
        with TempFile(
            mode='w+t', delete=False, prefix='mapping.', dir=CFG_DIR
        ) as tfile:
            with io.open(MAPPING_FILE, 'rt') as mapping_file:
                tfile.write(EDIT_HELP_COMMENTS + mapping_file.read())
            tfile.flush()
    except (OSError, IOError) as err:
        abort('dtags: failed to edit mapping: {}'.format(err), err.errno)
    else:
        editor = shlex.split(os.environ.get('EDITOR'))
        if not editor:
            abort('dtags: undefined environment variable: ' +
                  style.bad('EDITOR'))
        try:
            sp.check_call(editor + [tfile.name])
        except sp.CalledProcessError as err:
            abort('dtags: failed to edit mapping: {}'.format(err.message))
        else:
            mapping, excluded = parse_mapping(tfile.name)
            save_mapping(mapping)
            rm_files(tfile.name)
            if excluded:
                print('Cleaned the following entries:\n' + excluded + '\n')
            finish('New entries saved successfully')


def _clean(args):
    """Clean stale and/or invalid directories."""
    if args:
        abort(USAGE + 'dtags: too many arguments')
    mapping, excluded = load_mapping()
    if excluded:
        save_mapping(mapping)
        finish('Cleaned the following entries:\n' + excluded)
    else:
        save_mapping(mapping)
        finish('Nothing to clean')


def _list(targets=None, reverse=False):
    """List directories and tags.

    :param targets: the list of directories or tags to highlight
    :param reverse: whether to display the reverse mapping or not
    """
    if targets is None:
        targets = set()
    else:
        targets = set(targets)
        additional_targets = set()
        for target in targets:
            if target.startswith('-'):
                abort(USAGE + 'dtags: invalid argument: ' + style.bad(target))
            else:
                additional_targets.add(expand(target))
        targets.update(additional_targets)
    mapping, excluded = load_mapping()
    if excluded:
        print(
            'Found invalid entries in the mapping:\n' + excluded +
            '\nRun ' + style.cmd('dtags clean') + ' to remove them' + '\n'
        )
    if not mapping:
        finish('Nothing to list')
    msgs = []
    if reverse:
        if targets:
            mapping = {
                tag: paths for tag, paths in mapping.items()
                if tag in targets or paths & targets
            }
        for tag in sorted(mapping):
            lines = [style.tag(tag, tag in targets)]
            for path in sorted(mapping[tag]):
                lines.append(style.path(path, path in targets))
            msgs.append('\n'.join(lines))
        finish('\n\n'.join(msgs) if msgs else 'Nothing to list')
    else:
        rmapping = defaultdict(set)
        for tag, paths in mapping.items():
            for path in paths:
                rmapping[path].add(tag)
        if targets:
            rmapping = {
                path: tags for path, tags in rmapping.items()
                if path in targets or tags & targets
            }
        for path in sorted(rmapping):
            tags = ' '.join(
                style.tag(tag, tag in targets)
                for tag in sorted(rmapping[path])
            )
            msgs.append(style.path(path, path in targets) + ' ' + tags)
        finish('\n'.join(msgs) if msgs else 'Nothing to list')


def _commands(args):
    """Display all available commands."""
    if args:
        abort(USAGE + 'dtags: too many arguments')
    print(COMMANDS)


def manage():
    """Manage directory tags."""
    atexit.register(close_stdio)
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    args = sys.argv[1:]
    if not args:
        _list()
    head, tail = args[0], args[1:]
    if head == '--help':
        finish(USAGE + DESCRIPTION)
    elif head == '--version':
        finish('Version ' + VERSION)
    elif head == 'edit':
        _edit(tail)
    elif head == 'clean':
        _clean(tail)
    elif head == 'list':
        _list(tail, reverse=False)
    elif head == 'reverse':
        _list(tail, reverse=True)
    elif head == 'commands':
        _commands(tail)
    else:
        abort(USAGE + 'dtags: invalid argument: ' + style.bad(head))


def activate():
    """Write the shell runtime configuration to stdout."""
    atexit.register(close_stdio)
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    args = sys.argv[1:]
    if len(args) >= 2:
        abort(USAGE + 'dtags: too many arguments')
    if len(args) == 1:
        shell_name = args[0]
        config = SUPPORTED_SHELLS.get(shell_name)
        if config is None:
            abort('dtags: unsupported shell: ' + style.bad(shell_name))
    else:
        shell_path = os.environ.get('SHELL')
        if shell_path is None:
            abort('dtags: undefined environment variable: ' +
                  style.bad('SHELL'))
        shell_name = None
        for supported_shell_name in SUPPORTED_SHELLS:
            if supported_shell_name in shell_path:
                shell_name = supported_shell_name
        config = SUPPORTED_SHELLS.get(shell_name)
        if config is None:
            abort('dtags: unsupported shell: ' + style.bad(shell_path))
    finish(config.format(
        mapping_file=MAPPING_FILE,
        tags_file=TAGS_FILE,
        version=VERSION,
        usage=d.USAGE,
        description=d.DESCRIPTION,
        arg_err_tty=d.ARG_ERR_TTY,
        dest_err_tty=d.DEST_ERR_TTY,
        input_err_tty=d.INPUT_ERR_TTY,
        index_err_tty=d.INDEX_ERR_TTY,
        prompt_tty=d.PROMPT_TTY,
        choice_tty=d.CHOICE_TTY,
        arg_err=d.ARG_ERR,
        dest_err=d.DEST_ERR,
        input_err=d.INPUT_ERR,
        index_err=d.INDEX_ERR,
        prompt=d.PROMPT,
        choice=d.CHOICE,
    ))


def refresh():
    """Write the shell declare variable statements to stdout."""
    atexit.register(close_stdio)
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    args = sys.argv[1:]
    if len(args) >= 2:
        abort(USAGE + 'dtags: too many arguments')
    if len(args) == 1:
        shell_name = args[0]
        config = SUPPORTED_SHELLS.get(shell_name)
        if config is None:
            abort('dtags: unsupported shell: ' + style.bad(shell_name))
    else:
        shell_path = os.environ.get('SHELL')
        if shell_path is None:
            abort('dtags: undefined environment variable: ' +
                  style.bad('SHELL'))
        shell_name = None
        for supported_shell_name in SUPPORTED_SHELLS:
            if supported_shell_name in shell_path:
                shell_name = supported_shell_name
        config = SUPPORTED_SHELLS.get(shell_name)
        if config is None:
            abort('dtags: unsupported shell: ' + style.bad(shell_path))

    assign_string = 'set -g {} "{}"' if shell_name == 'fish' else '{}="{}"'
    mapping, _ = load_mapping()
    print('\n'.join(
        assign_string.format(tag.replace('-', '_'), paths.pop())
        for tag, paths in mapping.items()
        if len(paths) == 1 and
        tag.replace('-', '_') not in os.environ and
        not get_invalid_tag_chars(tag)
    ))




