"""Test all dtags commands

This is for internal development testing only.

Things that must be tested manually:

1. Run 'dtags edit'
2. Run 'd tag-with-many-dirs'
3. Kill 'e -p' and make sure child processes are dead
"""

from __future__ import unicode_literals

import io
import os
import shutil
import subprocess

import pytest

from dtags import CFG_DIR, MAPPING_FILE
from dtags.chars import TAG_CHARS
from dtags.version import VERSION
from dtags.commands import (
    directory as d,
    execute as e,
    manage as dt,
    tag as tg,
    untag as utg,
)

generated_tags = set()
tag_chars = list(TAG_CHARS)
home = os.path.expanduser('~')


def setup_module(*_):
    """Temporarily put away the user's dtags configuration."""
    shutil.move(CFG_DIR, CFG_DIR + '.backup')


def teardown_module(*_):
    """Restore the user's dtags configuration."""
    shutil.rmtree(CFG_DIR, ignore_errors=True)
    shutil.move(CFG_DIR + '.backup', CFG_DIR)


def run(command, shell=None):
    """Execute commands in the shell.

    :param command: the command to execute
    :param shell: the shell to use
    :return: the output of the command execution
    """
    kwargs = {
        'shell': True,
        'stderr': subprocess.STDOUT,
        'preexec_fn': os.setsid
    }
    if shell is None:
        shell = os.environ['SHELL']
    try:
        std_output = subprocess.check_output(
            '{} -i -c "{}"'.format(shell, command),
            **kwargs
        )
    except subprocess.CalledProcessError as err:
        return err.output
    else:
        return std_output


@pytest.mark.first
def test_init():
    """Test if the commands work as expected when no tags are defined"""
    expected = 'Nothing to list\n'
    assert run('dtags') == expected
    assert run('dtags list') == expected
    assert run('dtags list test') == expected
    assert run('dtags reverse') == expected
    assert run('dtags reverse test') == expected
    assert run('dtags clean') == 'Nothing to clean\n'


@pytest.mark.second
def test_tag():
    """Test if 'tag' works as expected."""
    # Test argument handling
    assert run('tag') == tg.USAGE + tg.DESCRIPTION + '\n'
    assert run('tag --help') == tg.USAGE + tg.DESCRIPTION + '\n'
    assert run('tag --version') == 'Version ' + VERSION + '\n'
    assert run('tag -z') == tg.USAGE + 'Invalid argument: -z\n'

    # Tag /usr/bin by basename
    assert run('tag /usr/bin') == '/usr/bin +#bin\n'
    assert run('dtags') == '/usr/bin #bin\n'
    assert run('tag /usr/bin') == 'Nothing to do\n'

    # Tag /usr/bin foo
    assert run('tag /usr/bin foo') == '/usr/bin +#foo\n'
    assert run('dtags') == '/usr/bin #bin #foo\n'
    assert run('tag /usr/bin foo bin') == 'Nothing to do\n'

    # Tag /usr/bin bar and baz
    assert run('tag /usr/bin bar baz') == '/usr/bin +#bar +#baz\n'
    assert run('dtags') == '/usr/bin #bar #baz #bin #foo\n'
    assert run('tag /usr/bin foo bar baz') == 'Nothing to do\n'

    # Tag /tmp by basename
    assert run('tag /tmp') == '/tmp +#tmp\n'
    assert '/tmp #tmp' in run('dtags')
    assert run('tag /tmp') == 'Nothing to do\n'

    # Tag ~ foo
    assert run('tag /tmp foo') == '/tmp +#foo\n'
    assert '/tmp #foo' in run('dtags')
    assert run('tag /tmp foo tmp') == 'Nothing to do\n'

    # Tag ~ bar and baz
    assert run('tag /tmp bar baz') == '/tmp +#bar +#baz\n'
    assert '/tmp #bar #baz #foo' in run('dtags')
    assert run('tag /tmp bar baz foo') == 'Nothing to do\n'

    # Test invalid arguments
    assert run("tag ~ 'a b'") == 'Tag name a b contains whitespaces\n'
    assert run('tag ~ b@d') == 'Tag name b@d contains bad characters @\n'
    assert run('tag ~ @x') == 'Tag name @x does not start with an alphabet\n'
    assert run('tag /@') == 'Directory path /@ contains bad characters @\n'
    assert run('tag /invalid') == 'Invalid directory /invalid\n'


@pytest.mark.third
def test_dtags():
    """Test if 'dtags' works as expected."""
    # Test argument handling
    assert run('dtags --help') == dt.USAGE + dt.DESCRIPTION + '\n'
    assert run('dtags --version') == 'Version ' + VERSION + '\n'
    assert run('dtags -z') == dt.USAGE + 'Invalid argument: -z\n'
    assert run('dtags list -z') == dt.USAGE + 'Invalid argument: -z\n'
    assert run('dtags edit invalid') == dt.USAGE + 'Too many arguments\n'
    assert run('dtags clean invalid') == dt.USAGE + 'Too many arguments\n'
    assert run('dtags shell bash bad') == dt.USAGE + 'Too many arguments\n'

    # Test 'dtags list'
    assert run('dtags list') == run('dtags')
    assert run('dtags list /tmp') == '/tmp #bar #baz #foo #tmp\n'
    assert run('dtags list /usr/bin') == '/usr/bin #bar #baz #bin #foo\n'
    output = run('dtags list foo')
    assert '/tmp' in output and '/usr/bin' in output
    output = run('dtags list tmp')
    assert '/tmp' in output and '/usr/bin' not in output
    output = run('dtags list bin')
    assert '/tmp' not in output and '/usr/bin' in output

    # Test 'dtags reverse'
    bar = '#bar\n/tmp\n/usr/bin\n'
    baz = '#baz\n/tmp\n/usr/bin\n'
    ubin = '#bin\n/usr/bin\n'
    foo = '#foo\n/tmp\n/usr/bin\n'
    tmp = '#tmp\n/tmp\n'
    assert run('dtags reverse') == '\n'.join([bar, baz, ubin, foo, tmp])
    assert run('dtags reverse tmp') == tmp
    assert run('dtags reverse bin') == ubin
    assert run('dtags reverse bar') == bar
    assert run('dtags reverse /usr/bin') == '\n'.join([bar, baz, ubin, foo])
    assert run('dtags reverse /tmp') == '\n'.join([bar, baz, foo, tmp])

    # Test 'dtags shell'
    assert '_dtags_dir=${_dtags_dirs[0]}' in run('dtags shell bash')
    assert '_dtags_dir=${_dtags_dirs[1]}' in run('dtags shell zsh')
    assert 'set _dtags_dir $_dtags_dirs[1]' in run('dtags shell fish')
    assert run('dtags shell bad') == 'Unsupported shell: bad\n'

    # Test sourcing 'dtags shell' output
    # assert execute('source <(dtags shell bash)', shell='bash') == ''
    assert run('source <(dtags shell zsh)', shell='zsh') == ''
    assert run('dtags shell fish | source', shell='fish') == ''

    # Test 'dtags clean' (safe version)
    assert run('dtags clean') == 'Nothing to clean\n'


@pytest.mark.fourth
def test_d():
    """Test if the 'd' command works as expected."""
    # Tag home directory to test the 'd' command
    assert run('tag ~ home') == '{} +#home\n'.format(home)

    # Test argument handling
    assert run('d --help') == d.USAGE + d.DESCRIPTION
    assert run('d --version') == 'Version ' + VERSION + '\n'
    assert run('d -z') == d.USAGE + 'Invalid argument: -z\n'
    assert run('d /tmp bad') == d.USAGE + 'Too many arguments\n'

    # Test changing directories
    d_msg = 'Going to {loc}...\n{loc}\n'
    assert run('d; pwd') == d_msg.format(loc=home)
    assert run('d home; pwd') == d_msg.format(loc=home)
    assert run('d tmp; pwd') == d_msg.format(loc='/tmp')


@pytest.mark.fifth
def test_e():
    """Test if the 'e' command works as expected."""
    # Test argument handling
    assert run('e') == e.USAGE + e.DESCRIPTION + '\n'
    assert run('e --help') == e.USAGE + e.DESCRIPTION + '\n'
    assert run('e --version') == 'Version ' + VERSION + '\n'
    assert run('e -z') == e.USAGE + 'Invalid argument: -z\n'
    assert run('e -p') == e.USAGE + 'Missing argument: <targets>\n'
    assert run('e test') == e.USAGE + 'Missing argument: <command>\n'
    assert run('e -p test') == e.USAGE + 'Missing argument: <command>\n'

    # Test executing commands
    s = 'Executing command pwd in sequence...\n\n'
    p = 'Executing command pwd in parallel...\n\n'
    m = 'in {loc}:\n{out}\nExit status: 0\n\n'
    assert run('e ~ pwd') == s + m.format(loc=home, out=home)
    assert run('e -p ~ pwd') == p + m.format(loc=home, out=home)
    assert run('e /tmp pwd') == s + m.format(loc='/tmp', out='/tmp')
    assert run('e -p /tmp pwd') == p + m.format(loc='/tmp', out='/tmp')
    assert run('e /tmp,~ pwd') == (
        s + m.format(loc=home, out=home) +
        m.format(loc='/tmp', out='/tmp')
    )
    assert run('e -p ~,/tmp pwd') == (
        p + m.format(loc=home, out=home) +
        m.format(loc='/tmp', out='/tmp')
    )
    assert run('e foo pwd') == (
        s + m.format(loc='/tmp #foo', out='/tmp') +
        m.format(loc='/usr/bin #foo', out='/usr/bin')
    )
    assert run('e -p foo pwd') == (
        p + m.format(loc='/tmp #foo', out='/tmp') +
        m.format(loc='/usr/bin #foo', out='/usr/bin')
    )
    output = run('e ~,foo pwd')
    assert s in output
    assert m.format(loc=home, out=home) in output
    assert m.format(loc='/tmp #foo', out='/tmp') in output
    assert m.format(loc='/usr/bin #foo', out='/usr/bin') in output
    output = run('e -p ~,foo pwd')
    assert p in output
    assert m.format(loc=home, out=home) in output
    assert m.format(loc='/tmp #foo', out='/tmp') in output
    assert m.format(loc='/usr/bin #foo', out='/usr/bin') in output


@pytest.mark.sixth
def test_untag():
    """Test if 'untag' works as expected."""
    # Test argument handling
    assert run('untag') == utg.USAGE + utg.DESCRIPTION + '\n'
    assert run('untag --help') == utg.USAGE + utg.DESCRIPTION + '\n'
    assert run('untag --version') == 'Version ' + VERSION + '\n'
    assert run('untag -z') == utg.USAGE + 'Invalid argument: -z\n'

    # Remove tag from home directory
    assert run('untag ~') == '{} -#home\n'.format(home)
    assert home not in run('dtags list')
    assert home not in run('dtags reverse')

    # Remove tag foo from /usr/bin
    assert run('untag /usr/bin foo') == '/usr/bin -#foo\n'
    assert run('untag /usr/bin foo') == 'Nothing to do\n'
    assert '/usr/bin' not in run('dtags list foo')
    assert 'foo' not in run('dtags list /usr/bin')

    # Remove tag bar and an unknown tag from /usr/bin
    assert run('untag /usr/bin bar unknown') == '/usr/bin -#bar\n'
    assert '/usr/bin' not in run('dtags list foo bar')
    assert 'bar' not in run('dtags list /usr/bin')

    # Remove the rest of the tags from /usr/bin
    assert run('untag /usr/bin bin baz') == '/usr/bin -#baz -#bin\n'
    assert run('dtags list /usr/bin') == 'Nothing to list\n'
    assert '/usr/bin' not in run('dtags list foo bar baz')

    # Remove all tags from /tmp at once
    assert run('untag /tmp') == '/tmp -#bar -#baz -#foo -#tmp\n'
    assert run('dtags list /tmp') == 'Nothing to list\n'
    assert run('dtags list foo bar baz') == 'Nothing to list\n'


@pytest.mark.last
def test_bad_mapping():
    """Test if bad mapping is handled properly."""
    assert run('dtags clean') == 'Nothing to clean\n'
    test_mapping = """
    # This line should be ignored
    \t~,has whitespace, home
      ~,_no_leading_alpha
    ~,has_inv@lid_char
    /has_inv@lid,valid_tag
    /has_no_tags,

    ~, foo,bar , baz ,
    \t/tmp,foo,bar,baz  ,tmp
    """
    with io.open(MAPPING_FILE, "w+t") as open_file:
        open_file.write(test_mapping)

    expected_errors = [
      '> has_inv@lid_char contains bad characters: @',
      '> _no_leading_alpha does not start with an alphabet',
      '> /has_inv@lid contains bad characters: @',
      '> has whitespace contains whitespaces',
      '> /has_no_tags is not mapped to any valid tags'
    ]
    # Test 'e'
    for output in [run('e ~ pwd'), run('e -p ~ pwd')]:
        for expected_error in expected_errors:
            assert expected_error in output

    # Test 'dtags'
    for output in [run('dtags'), run('dtags list'), run('dtags reverse')]:
        for expected_error in expected_errors:
            assert expected_error in output
            assert 'Run dtags clean to remove them' in output
    output = run('dtags')
    assert '/tmp #bar #baz #foo #tmp' in output
    assert '{} #bar #baz #foo #home'.format(home) in output

    # Test 'tag'
    output = run('tag /tmp')
    for expected_error in expected_errors:
        assert expected_error in output
    assert 'Nothing to do' in output
    assert 'Cleaned the following invalid entries' in output
    output = run('tag /tmp')
    for expected_error in expected_errors:
        assert expected_error not in output
    assert 'Cleaned the following invalid entries' not in output

    # Test 'untag'
    with io.open(MAPPING_FILE, "w+t") as open_file:
        open_file.write(test_mapping)
    output = run('untag /tmp')
    for expected_error in expected_errors:
        assert expected_error in output
    assert '/tmp -#bar -#baz -#foo -#tmp' in output
    assert 'Cleaned the following invalid entries' in output
    output = run('untag /tmp')
    for expected_error in expected_errors:
        assert expected_error not in output
    assert 'Cleaned the following invalid entries' not in output
    assert 'Nothing to do' in output
