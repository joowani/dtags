from string import punctuation

from dtags.commons import (
    normalize_dir,
    normalize_dirs,
    normalize_tag,
    normalize_tags,
    reverse_map,
)


def test_reverse_map(dir1, dir2):
    config = {dir2: set()}
    assert reverse_map(config) == {}

    config = {dir2: {"dir1"}, dir1: {"dir1"}}
    assert reverse_map(config) == {"dir1": {dir2, dir1}}

    config = {dir2: {"dir1", "dir2"}}
    assert reverse_map(config) == {"dir1": {dir2}, "dir2": {dir2}}


def test_normalize_dir(dir1, dir2):
    assert normalize_dir(dir1.as_posix()) == dir1
    assert normalize_dir(dir2.as_posix()) == dir2
    assert normalize_dir("foobar") is None


def test_normalize_dirs(dir1, dir2):
    assert normalize_dirs(None) == set()
    assert normalize_dirs([]) == set()
    assert normalize_dirs(["dir1", "dir2"]) == set()
    assert normalize_dirs([dir2.as_posix()]) == {dir2}

    dirs = [dir2.as_posix(), dir2.as_posix()]
    assert normalize_dirs(dirs) == {dir2}

    dirs = [dir2.as_posix(), dir1.as_posix()]
    assert normalize_dirs(dirs) == {dir2, dir1}


def test_normalize_tag():
    assert normalize_tag(punctuation) == ""
    assert normalize_tag("abc") == "abc"
    assert normalize_tag("ABC") == "ABC"
    assert normalize_tag("Foo Bar") == "Foo-Bar"
    assert normalize_tag("FoO_BaR") == "FoO-BaR"
    assert normalize_tag("1234567") == "1234567"
    assert normalize_tag("1foobar") == "1foobar"


def test_normalize_tags():
    assert normalize_tags(None) == set()
    assert normalize_tags([]) == set()
    assert normalize_tags(["dir1", "dir2"]) == {"dir1", "dir2"}
    assert normalize_tags(["dir1", punctuation]) == {"dir1"}
