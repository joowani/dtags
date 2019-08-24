"""This module is for internal development testing only!!!

Note to self: things that must be tested manually:

1. Run 'dtags edit'
2. Run 'd tag-with-many-dirs'
3. Kill a running 'p' command and ensure the child processes are dead
4. Check if shell variables are automatically created on tagging
"""

from __future__ import unicode_literals

import io
import os
import locale
import shutil
import subprocess

from dtags import CFG_DIR, MAPPING_FILE
from dtags.chars import TAG_CHARS
from dtags.version import VERSION
from dtags.commands import t, u, d, e, p
from dtags.commands import (
    USAGE,
    DESCRIPTION,
    COMMANDS
)

encoding = locale.getdefaultlocale()[1]
generated_tags = set()
tag_chars = list(TAG_CHARS)
home = os.path.expanduser('~')
current_shell = os.environ.get('SHELL', '')

dir1, tag1 = '', ''
dir2, tag2 = '', ''
bad_dir = ''


def generate_dirname():
    num = 0
    existing = os.listdir(home)
    dirname = 'dtags_test{num:03d}'.format(num=num)
    while dirname in existing:
        num += 1
        dirname = 'dtags_test{num:03d}'.format(num=num)
    return os.path.join(home, dirname)


def setup_module(*_):
    """Temporarily put away the user's dtags configuration."""
    global dir1, dir2, bad_dir, tag1, tag2

    dir1 = generate_dirname()
    tag1 = os.path.basename(dir1)
    os.mkdir(dir1)
    os.mkdir(os.path.join(dir1, 'subdir01'))

    dir2 = generate_dirname()
    tag2 = os.path.basename(dir2)
    os.mkdir(dir2)
    os.mkdir(os.path.join(dir2, 'subdir02'))

    bad_dir = generate_dirname()
    shutil.move(CFG_DIR, CFG_DIR + '.backup')


def teardown_module(*_):
    """Restore the user's dtags configuration."""
    shutil.rmtree(CFG_DIR, ignore_errors=True)
    shutil.move(CFG_DIR + '.backup', CFG_DIR)
    shutil.rmtree(dir1, ignore_errors=True)
    shutil.rmtree(dir2, ignore_errors=True)


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
    valid_output_lines = []
    if shell is None:
        shell = current_shell
    try:
        std_output = subprocess.check_output(
            '{} -i -c "{}"'.format(shell, command),
            **kwargs
        )
    except subprocess.CalledProcessError as err:
        for line in err.output.decode(encoding).split('\n'):
            if 'cannot set terminal' in line or 'no job control' in line:
                continue
            valid_output_lines.append(line)
    else:
        for line in std_output.decode(encoding).split('\n'):
            if 'cannot set terminal' in line or 'no job control' in line:
                continue
            valid_output_lines.append(line)
    return '\n'.join(valid_output_lines)


def test_init():
    """Test if the commands work as expected when no tags are defined"""
    expected = 'Nothing to list\n'
    assert run('dtags') == expected
    assert run('dtags list') == expected
    assert run('dtags list test') == expected
    assert run('dtags reverse') == expected
    assert run('dtags reverse test') == expected
    assert run('dtags commands') == COMMANDS + '\n'
    assert run('dtags clean') == 'Nothing to clean\n'


def test_t():
    """Test if 'tag' works as expected."""
    # Test basic argument handling
    assert run('t') == t.USAGE + t.DESCRIPTION + '\n'
    assert run('t --help') == t.USAGE + t.DESCRIPTION + '\n'
    assert run('t --version') == 'Version ' + VERSION + '\n'

    # Test invalid arguments
    if 'zsh' in current_shell or 'fish' in current_shell:
        assert run("t ~ 'a b'") == 't: tag name a b contains whitespaces\n'
    assert run('t ~ b@d') == 't: tag name b@d contains bad characters @\n'
    assert run('t ~ @x') == 't: tag name @x does not start with an alphabet\n'
    assert run('t /@') == 't: directory path /@ contains bad characters @\n'
    expected = 't: invalid directory: {}\n'.format(bad_dir)
    assert run('t {}'.format(bad_dir)) == expected

    # Tag test directory 01 by basename
    assert run('t {}'.format(dir1)) == '{} +#{}\n'.format(dir1, tag1)
    assert run('dtags') == '{} #{}\n'.format(dir1, tag1)
    assert run('t {}'.format(dir1)) == 'Nothing to do\n'

    # Tag test directory 01 'foo'
    assert run('t {} foo'.format(dir1)) == '{} +#foo\n'.format(dir1)
    assert run('dtags') == '{} #{} #foo\n'.format(dir1, tag1)
    assert run('t {} {} foo'.format(dir1, tag1)) == 'Nothing to do\n'

    # Tag test directory 01 'bar' and 'baz'
    expected = '{} +#bar +#baz\n'.format(dir1)
    assert run('t {} bar baz'.format(dir1)) == expected
    assert run('dtags') == '{} #bar #baz #{} #foo\n'.format(dir1, tag1)
    assert run('t {} {} foo bar baz'.format(dir1, tag1)) == 'Nothing to do\n'

    # Tag test directory 02 by basename
    assert run('t {}'.format(dir2)) == '{} +#{}\n'.format(dir2, tag2)
    assert '{} #{}\n'.format(dir2, tag2) in run('dtags')
    assert run('t {}'.format(dir2)) == 'Nothing to do\n'

    # Tag test directory 02 'foo'
    assert run('t {} foo'.format(dir2)) == '{} +#foo\n'.format(dir2)
    assert '{} #{} #foo\n'.format(dir2, tag2) in run('dtags')
    assert run('t {} {} foo'.format(dir2, tag2)) == 'Nothing to do\n'

    # Tag test directory 02 'bar' and 'baz'
    expected = '{} +#bar +#baz\n'.format(dir2)
    assert run('t {} bar baz'.format(dir2)) == expected
    assert '{} #bar #baz #{} #foo\n'.format(dir2, tag2) in run('dtags')
    assert run('t {} {} bar baz foo'.format(dir2, tag2)) == 'Nothing to do\n'


def test_dtags():
    """Test if 'dtags' works as expected."""
    # Test basic argument handling
    assert run('dtags --help') == USAGE + DESCRIPTION + '\n'
    assert run('dtags --version') == 'Version ' + VERSION + '\n'
    assert run('dtags -z') == USAGE + 'dtags: invalid argument: -z\n'
    assert run('dtags list -z') == USAGE + 'dtags: invalid argument: -z\n'
    assert run('dtags edit invalid') == USAGE + 'dtags: too many arguments\n'
    assert run('dtags clean invalid') == USAGE + 'dtags: too many arguments\n'
    assert run('dtags commands bad') == USAGE + 'dtags: too many arguments\n'

    # Test 'dtags list'
    assert run('dtags list') == run('dtags')
    assert run('dtags list invalid') == 'Nothing to list\n'
    expected = '{} #bar #baz #{} #foo\n'.format(dir1, tag1)
    assert run('dtags list {}'.format(dir1)) == expected
    expected = '{} #bar #baz #{} #foo\n'.format(dir2, tag2)
    assert run('dtags list {}'.format(dir2)) == expected
    for tag in ['foo', 'bar', 'baz']:
        output = run('dtags list {}'.format(tag))
        assert dir1 in output and dir2 in output
    for tag in ['bad', 'bin', 'usr', home]:
        output = run('dtags list {}'.format(tag))
        assert dir1 not in output and dir2 not in output

    # Test 'dtags reverse'
    foo = '#foo\n{}\n{}\n'.format(dir1, dir2)
    bar = '#bar\n{}\n{}\n'.format(dir1, dir2)
    baz = '#baz\n{}\n{}\n'.format(dir1, dir2)
    t1 = '#{}\n{}\n'.format(tag1, dir1)
    t2 = '#{}\n{}\n'.format(tag2, dir2)
    assert run('dtags reverse') == '\n'.join([bar, baz, t1, t2, foo])
    assert run('dtags reverse foo') == foo
    assert run('dtags reverse bar') == bar
    assert run('dtags reverse baz') == baz
    expected_output = '\n'.join([bar, baz, t1, foo])
    assert run('dtags reverse {}'.format(dir1)) == expected_output
    expected_output = '\n'.join([bar, baz, t2, foo])
    assert run('dtags reverse {}'.format(dir2)) == expected_output

    # Test 'dtags clean' (safe version)
    assert run('dtags clean') == 'Nothing to clean\n'

    # Test 'dtags-activate'
    assert '_dtags_dir=${_dtags_dirs[0]}' in run('dtags-activate bash')
    assert '_dtags_dir=${_dtags_dirs[1]}' in run('dtags-activate zsh')
    assert 'set _dtags_dir $_dtags_dirs[1]' in run('dtags-activate fish')
    assert run('dtags-activate bad') == 'dtags: unsupported shell: bad\n'

    # Test sourcing the output of 'dtags-activate'
    if 'bash' in current_shell:
        assert run('source <(dtags-activate bash)', shell='bash') == ''
    if 'zsh' in current_shell:
        assert run('. <(dtags-activate zsh)', shell='zsh') == ''
    if 'fish' in current_shell:
        assert run('dtags-activate fish | source', shell='fish') == ''

    # Test 'dtags-refresh'
    fish_refresh_output = run('dtags-refresh fish')
    assert 'set -g {} "{}"'.format(tag1, dir1) in fish_refresh_output
    assert 'set -g {} "{}"'.format(tag2, dir2) in fish_refresh_output

    bash_refresh_output = run('dtags-refresh bash')
    assert '{}="{}"'.format(tag1, dir1) in bash_refresh_output
    assert '{}="{}"'.format(tag2, dir2) in bash_refresh_output

    zsh_refresh_output = run('dtags-refresh zsh')
    assert '{}="{}"'.format(tag1, dir1) in zsh_refresh_output
    assert '{}="{}"'.format(tag2, dir2) in zsh_refresh_output

    # Test sourcing the output of 'dtags-refresh'
    if 'bash' in current_shell:
        assert run('. <(dtags-refresh bash)', shell='bash') == ''
    elif 'zsh' in current_shell:
        assert run('. <(dtags-refresh zsh)', shell='zsh') == ''
    elif 'fish' in current_shell:
        assert run('dtags-refresh fish | source', shell='fish') == ''


def test_d():
    """Test if the 'd' command works as expected."""
    # Test basic argument handling
    assert run('d --help') == d.USAGE + d.DESCRIPTION
    assert run('d --version') == 'Version ' + VERSION + '\n'
    assert run('d too many args') == d.USAGE + 'd: too many arguments\n'

    # Test changing directories
    assert home in run('d; pwd')
    assert dir1 in run('d {}; pwd'.format(tag1))
    assert home in run('d -; pwd')
    assert dir2 in run('d {}; pwd'.format(tag2))
    assert dir1 in run('d {}; pwd'.format(dir1))
    assert dir2 in run('d {}; pwd'.format(dir2))

    expected_error = 'd: invalid destination: {}\n'.format(bad_dir)
    assert run('d {}'.format(bad_dir)) == expected_error


def test_e():
    """Test if the 'e' command works as expected."""
    # Test argument handling
    assert run('e') == e.USAGE + e.DESCRIPTION + '\n'
    assert run('e --help') == e.USAGE + e.DESCRIPTION + '\n'
    assert run('e --version') == 'Version ' + VERSION + '\n'
    assert run('e -z') == e.USAGE + 'e: invalid argument: -z\n'
    assert run('e -i') == e.USAGE + 'e: missing argument: <targets>\n'
    assert run('e test') == e.USAGE + 'e: missing argument: <command>\n'
    assert run('e -i test') == e.USAGE + 'e: missing argument: <command>\n'

    # Test executing commands
    l = '\n'  # newline
    m = 'in {loc}:\n{out}\n\n\n'
    for dst in [home, dir1, dir2]:
        assert run('e {} pwd'.format(dst)) == l + m.format(loc=dst, out=dst)
        assert run('e -i {} pwd'.format(dst)) == l + m.format(loc=dst, out=dst)

    assert run('e {} pwd'.format(tag1)) == (
        l + m.format(loc='{} #{}'.format(dir1, tag1), out=dir1)
    )
    assert run('e -i {} pwd'.format(tag1)) == (
        l + m.format(loc='{} #{}'.format(dir1, tag1), out=dir1)
    )
    for output in [run('e ~,foo pwd'), run('e -i ~,foo pwd')]:
        assert m.format(loc=home, out=home) in output
        assert m.format(loc='{} #foo'.format(dir1), out=dir1) in output
        assert m.format(loc='{} #foo'.format(dir2), out=dir2) in output


def test_p():
    """Test if the 'e' command works as expected."""
    # Test argument handling
    assert run('p') == p.USAGE + p.DESCRIPTION + '\n'
    assert run('p --help') == p.USAGE + p.DESCRIPTION + '\n'
    assert run('p --version') == 'Version ' + VERSION + '\n'
    assert run('p -z') == p.USAGE + 'p: invalid argument: -z\n'
    assert run('p -i') == p.USAGE + 'p: missing argument: <targets>\n'
    assert run('p test') == p.USAGE + 'p: missing argument: <command>\n'
    assert run('p -i test') == p.USAGE + 'p: missing argument: <command>\n'

    # Test executing commands
    l = '\n'  # newline
    m = 'in {loc}:\n{out}\n\n\n'
    for dst in [home, dir1, dir2]:
        assert run('p {} pwd'.format(dst)) == l + m.format(loc=dst, out=dst)
        assert run('p -i {} pwd'.format(dst)) == l + m.format(loc=dst, out=dst)

    assert run('p {} pwd'.format(tag1)) == (
        l + m.format(loc='{} #{}'.format(dir1, tag1), out=dir1)
    )
    assert run('p -i {} pwd'.format(tag1)) == (
        l + m.format(loc='{} #{}'.format(dir1, tag1), out=dir1)
    )
    for output in [run('p ~,foo pwd'), run('p -i ~,foo pwd')]:
        assert m.format(loc=home, out=home) in output
        assert m.format(loc='{} #foo'.format(dir1), out=dir1) in output
        assert m.format(loc='{} #foo'.format(dir2), out=dir2) in output


def test_u():
    """Test if 'untag' works as expected."""
    # Test basic argument handling
    assert run('u') == u.USAGE + u.DESCRIPTION + '\n'
    assert run('u --help') == u.USAGE + u.DESCRIPTION + '\n'
    assert run('u --version') == 'Version ' + VERSION + '\n'
    assert run('u {}'.format(bad_dir)) == 'Nothing to do\n'

    # Remove tag 'foo' from test directory 01
    assert run('u {} foo'.format(dir1)) == '{} -#foo\n'.format(dir1)
    assert run('u {} foo'.format(dir1)) == 'Nothing to do\n'
    assert dir1 not in run('dtags list foo')
    assert 'foo' not in run('dtags list {}'.format(dir1))

    # Remove tag 'bar' and an unknown tag from test directory 01
    assert run('u {} bar unknown'.format(dir1)) == '{} -#bar\n'.format(dir1)
    assert dir1 not in run('dtags list foo bar')
    assert 'bar' not in run('dtags list {}'.format(dir1))

    # Remove the rest of the tags from /usr/bin
    expected_output = '{} -#baz -#{}\n'.format(dir1, tag1)
    assert run('u {} {} baz'.format(dir1, tag1)) == expected_output
    assert run('dtags list {}'.format(dir1)) == 'Nothing to list\n'
    assert run('dtags list {}'.format(tag1)) == 'Nothing to list\n'
    assert dir1 not in run('dtags list foo bar baz {}'.format(tag1))

    # Remove all tags from /tmp at once
    expected_output = '{} -#bar -#baz -#{} -#foo\n'.format(dir2, tag2)
    assert run('u {}'.format(dir2)) == expected_output
    assert run('dtags list {}') == 'Nothing to list\n'
    assert run('dtags list {} foo bar baz'.format(tag1)) == 'Nothing to list\n'


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
    output = run('t /tmp')
    for expected_error in expected_errors:
        assert expected_error in output
    assert 'Nothing to do' in output
    assert 'Cleaned the following invalid entries' in output
    output = run('t /tmp')
    for expected_error in expected_errors:
        assert expected_error not in output
    assert 'Cleaned the following invalid entries' not in output

    # Test 'untag'
    with io.open(MAPPING_FILE, "w+t") as open_file:
        open_file.write(test_mapping)
    output = run('u /tmp')
    for expected_error in expected_errors:
        assert expected_error in output
    assert '/tmp -#bar -#baz -#foo -#tmp' in output
    assert 'Cleaned the following invalid entries' in output
    output = run('u /tmp')
    for expected_error in expected_errors:
        assert expected_error not in output
    assert 'Cleaned the following invalid entries' not in output
    assert 'Nothing to do' in output
