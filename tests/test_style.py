from dtags import style as s

from .helpers import clean_str


def test_style_tag():
    assert clean_str(s.tag("a", tty=False)) == "@a"
    assert clean_str(s.tag("b", tty=False)) == "@b"
    assert clean_str(s.tag("a", tty=True)) == "@a"
    assert clean_str(s.tag("b", tty=True)) == "@b"


def test_style_path(dir1, dir2):
    assert clean_str(s.path(dir1, tty=False)) == dir1.as_posix()
    assert clean_str(s.path(dir2, tty=False)) == dir2.as_posix()
    assert clean_str(s.path(dir1, tty=True)) == dir1.as_posix()
    assert clean_str(s.path(dir2, tty=True)) == dir2.as_posix()


def test_style_command():
    assert clean_str(s.command("ls -la", tty=False)) == "$ ls -la"
    assert clean_str(s.command("ps aux", tty=False)) == "$ ps aux"
    assert clean_str(s.command("ls -la", tty=True)) == "$ ls -la"
    assert clean_str(s.command("ps aux", tty=True)) == "$ ps aux"


def test_style_dir_tags(dir1):
    expected = f"{dir1.as_posix()} @a @b"
    assert clean_str(s.mapping(dir1, {"a", "b"}, tty=False)) == expected
    assert clean_str(s.mapping(dir1, {"a", "b"}, tty=True)) == expected

    expected = f"{dir1.as_posix()}"
    assert clean_str(s.mapping(dir1, set(), tty=False)) == expected
    assert clean_str(s.mapping(dir1, set(), tty=True)) == expected


def test_style_dir_tags_diff(dir1):
    expected = f"{dir1.as_posix()}"
    assert clean_str(s.diff(dir1, set(), set(), tty=False)) == expected
    assert clean_str(s.diff(dir1, set(), set(), tty=True)) == expected

    expected = f"{dir1.as_posix()} +@a +@b"
    assert clean_str(s.diff(dir1, {"a", "b"}, set(), tty=False)) == expected
    assert clean_str(s.diff(dir1, {"a", "b"}, set(), tty=True)) == expected

    expected = f"{dir1.as_posix()} -@c -@d"
    assert clean_str(s.diff(dir1, set(), {"c", "d"}, tty=False)) == expected
    assert clean_str(s.diff(dir1, set(), {"c", "d"}, tty=True)) == expected

    expected = f"{dir1.as_posix()} +@a +@b -@c -@d"
    assert clean_str(s.diff(dir1, {"a", "b"}, {"c", "d"}, tty=False)) == expected
    assert clean_str(s.diff(dir1, {"a", "b"}, {"c", "d"}, tty=True)) == expected
