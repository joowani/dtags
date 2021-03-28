import shutil
from string import whitespace
from typing import List

from dtags.commands import activate, d, run, tag, tags, untag
from dtags.files import CONFIG_FILE, get_file_path

from .helpers import clean_str, load_completion, load_destination


def normalize_str(value) -> List[str]:
    lines = value.splitlines(keepends=False) if isinstance(value, str) else value
    return [l for l in map(lambda x: clean_str(x).strip(whitespace), lines) if l]


def assert_stdout(capture, expected):
    assert normalize_str(capture.readouterr().out) == normalize_str(expected)


def assert_stderr(capture, expected):
    assert normalize_str(capture.readouterr().err) == normalize_str(expected)


def test_invalid_config(capsys):
    config = get_file_path(CONFIG_FILE)
    config.parent.mkdir()

    with open(get_file_path(CONFIG_FILE), "w") as fp:
        fp.write("foobar")

    tags.execute([])
    assert_stderr(
        capsys,
        f"Bad data in {config.as_posix()}: Expecting value: line 1 column 1 (char 0)",
    )


def test_command_activate(capsys):
    activate.execute(["bash"])
    assert_stdout(capsys, activate.BASH_ACTIVATE_SCRIPT)

    activate.execute(["zsh"])
    assert_stdout(capsys, activate.ZSH_ACTIVATE_SCRIPT)

    activate.execute(["fish"])
    assert_stdout(capsys, activate.FISH_ACTIVATE_SCRIPT)

    activate.execute([])
    assert_stderr(
        capsys,
        f"""
        usage: {activate.USAGE}
        dtags-activate: error: the following arguments are required: shell
        """,
    )


def test_command_d(capsys, dir1, dir2, dir3, monkeypatch):
    d.execute([])
    assert_stderr(
        capsys,
        f"""
        usage: {d.USAGE}
        d: error: the following arguments are required: DEST
        """,
    )
    d.execute([dir1.as_posix()])
    assert load_destination() == dir1.as_posix()

    d.execute([dir2.as_posix()])
    assert load_destination() == dir2.as_posix()

    d.execute([dir3.as_posix()])
    assert load_destination() == dir3.as_posix()

    d.execute(["foo"])
    assert_stderr(capsys, "Invalid destination: foo")

    tag.execute([dir1.as_posix(), "-t", "foo", "-y"])
    assert_stdout(
        capsys,
        f"""
        {dir1.as_posix()} +@foo
        Tags saved successfully
        """,
    )
    d.execute(["foo"])
    assert_stderr(capsys, "")
    assert load_destination() == dir1.as_posix()


def test_command_tag(capsys, dir1, dir2, dir3):
    tag.execute([dir3.as_posix(), dir2.as_posix(), dir1.as_posix(), "-y"])
    assert_stdout(
        capsys,
        f"""
        {dir1.as_posix()} +@{dir1.name}
        {dir2.as_posix()} +@{dir2.name}
        {dir3.as_posix()} +@{dir3.name}
        Tags saved successfully
        """,
    )
    assert load_completion() == [dir1.name, dir2.name, dir3.name]
    tag.execute([dir3.as_posix(), dir2.as_posix(), dir1.as_posix(), "-y", "-t", "foo"])
    assert_stdout(
        capsys,
        f"""
        {dir1.as_posix()} +@foo
        {dir2.as_posix()} +@foo
        {dir3.as_posix()} +@foo
        Tags saved successfully
        """,
    )
    assert load_completion() == [dir1.name, dir2.name, dir3.name, "foo"]
    tag.execute([dir1.as_posix(), "-y"])
    assert_stdout(
        capsys,
        "Nothing to do",
    )
    tags.execute([])
    assert_stdout(
        capsys,
        f"""
        {dir1.as_posix()} @{dir1.name} @foo
        {dir2.as_posix()} @{dir2.name} @foo
        {dir3.as_posix()} @{dir3.name} @foo
        """,
    )


def test_command_untag(capsys, dir1, dir2, dir3):
    tag.execute([dir3.as_posix(), dir2.as_posix(), dir1.as_posix(), "-y"])
    assert_stdout(
        capsys,
        f"""
        {dir1.as_posix()} +@{dir1.name}
        {dir2.as_posix()} +@{dir2.name}
        {dir3.as_posix()} +@{dir3.name}
        Tags saved successfully
        """,
    )
    tag.execute([dir3.as_posix(), dir2.as_posix(), dir1.as_posix(), "-y", "-t", "foo"])
    assert_stdout(
        capsys,
        f"""
        {dir1.as_posix()} +@foo
        {dir2.as_posix()} +@foo
        {dir3.as_posix()} +@foo
        Tags saved successfully
        """,
    )
    assert load_completion() == [dir1.name, dir2.name, dir3.name, "foo"]
    untag.execute([])
    assert_stderr(
        capsys,
        f"""
        usage: {untag.USAGE}
        untag: error: one of the following arguments are required: DIR, -t
        """,
    )
    untag.execute([dir1.as_posix(), "-y"])
    assert_stdout(
        capsys,
        f"""
        {dir1.as_posix()} -@{dir1.name} -@foo
        Tags removed successfully
        """,
    )
    tags.execute([])
    assert_stdout(
        capsys,
        f"""
        {dir2.as_posix()} @{dir2.name} @foo
        {dir3.as_posix()} @{dir3.name} @foo
        """,
    )
    assert load_completion() == [dir2.name, dir3.name, "foo"]
    untag.execute(["-y", "-t", "foo"])
    assert_stdout(
        capsys,
        f"""
        {dir2.as_posix()} -@foo
        {dir3.as_posix()} -@foo
        Tags removed successfully
        """,
    )
    assert load_completion() == [dir2.name, dir3.name]
    untag.execute(["-y", dir2.as_posix(), dir3.as_posix()])
    assert_stdout(
        capsys,
        f"""
        {dir2.as_posix()} -@{dir2.name}
        {dir3.as_posix()} -@{dir3.name}
        Tags removed successfully
        """,
    )
    assert load_completion() == []
    untag.execute(["-y", dir3.as_posix(), dir2.as_posix(), dir1.as_posix()])
    assert_stdout(capsys, "Nothing to do")


def test_command_run(capsys, dir1, dir2, dir3):
    tag.execute([dir3.as_posix(), dir2.as_posix(), dir1.as_posix(), "-y"])
    assert_stdout(
        capsys,
        f"""
        {dir1.as_posix()} +@{dir1.name}
        {dir2.as_posix()} +@{dir2.name}
        {dir3.as_posix()} +@{dir3.name}
        Tags saved successfully
        """,
    )
    tag.execute([dir3.as_posix(), dir2.as_posix(), dir1.as_posix(), "-y", "-t", "foo"])
    assert_stdout(
        capsys,
        f"""
        {dir1.as_posix()} +@foo
        {dir2.as_posix()} +@foo
        {dir3.as_posix()} +@foo
        Tags saved successfully
        """,
    )
    run.execute(["foo", "--cmd"])
    assert_stderr(
        capsys,
        f"""
        usage: {run.USAGE}
        run: error: the following arguments are required: -c/--cmd
        """,
    )
    run.execute(["foo", "--cmd", "ls"])
    assert_stdout(
        capsys,
        f"""
        {dir1.as_posix()} @{dir1.name} @foo:
        {dir2.as_posix()} @{dir2.name} @foo:
        {dir3.as_posix()} @{dir3.name} @foo:
        """,
    )
    for directory in [dir1, dir2, dir3]:
        run.execute([directory.name, "-c", "ls"])
        assert_stdout(capsys, f"{directory.as_posix()} @{directory.name} @foo:")

        run.execute([directory.as_posix(), "-c", "ls"])
        assert_stdout(capsys, f"{directory.as_posix()} @{directory.name} @foo:")

        run.execute([directory.as_posix(), "-c", "foobar"])
        assert_stdout(capsys, f"{directory.as_posix()} @{directory.name} @foo:")

        run.execute([directory.as_posix(), "-c", "ls", "foobar"])
        assert_stdout(capsys, f"{directory.as_posix()} @{directory.name} @foo:")

    run.execute(["bar", "-c", "ls"])
    assert_stdout(capsys, "")


def test_command_tags(capsys, dir1, dir2, dir3):
    tag.execute([dir3.as_posix(), dir2.as_posix(), dir1.as_posix(), "-y"])
    assert_stdout(
        capsys,
        f"""
        {dir1.as_posix()} +@{dir1.name}
        {dir2.as_posix()} +@{dir2.name}
        {dir3.as_posix()} +@{dir3.name}
        Tags saved successfully
        """,
    )
    tag.execute([dir3.as_posix(), dir2.as_posix(), dir1.as_posix(), "-y", "-t", "foo"])
    assert_stdout(
        capsys,
        f"""
        {dir1.as_posix()} +@foo
        {dir2.as_posix()} +@foo
        {dir3.as_posix()} +@foo
        Tags saved successfully
        """,
    )
    tags.execute(["--reverse", "--clean"])
    assert_stderr(
        capsys,
        f"""
        usage: {tags.USAGE}
        tags: error: argument -r/--reverse: not allowed with argument -c/--clean
        """,
    )

    tags.execute(["--reverse", "--purge"])
    assert_stderr(
        capsys,
        f"""
        usage: {tags.USAGE}
        tags: error: argument -r/--reverse: not allowed with argument -p/--purge
        """,
    )

    tags.execute(["--json", "--clean"])
    assert_stderr(
        capsys,
        f"""
        usage: {tags.USAGE}
        tags: error: argument -j/--json: not allowed with argument -c/--clean
        """,
    )
    tags.execute(["--json", "--purge"])
    assert_stderr(
        capsys,
        f"""
        usage: {tags.USAGE}
        tags: error: argument -j/--json: not allowed with argument -p/--purge
        """,
    )
    tags.execute()
    assert_stdout(
        capsys,
        f"""
        {dir1.as_posix()} @{dir1.name} @foo
        {dir2.as_posix()} @{dir2.name} @foo
        {dir3.as_posix()} @{dir3.name} @foo
        """,
    )
    tags.execute(["--json"])
    assert_stdout(
        capsys,
        f"""
        {{
          "{dir1.as_posix()}": [
            "{dir1.name}",
            "foo"
          ],
          "{dir2.as_posix()}": [
            "{dir2.name}",
            "foo"
          ],
          "{dir3.as_posix()}": [
            "{dir3.name}",
            "foo"
          ]
        }}
        """,
    )
    tags.execute(["--reverse"])
    assert_stdout(
        capsys,
        f"""
        @{dir1.name}
          {dir1.as_posix()}
        @{dir2.name}
          {dir2.as_posix()}
        @{dir3.name}
          {dir3.as_posix()}
        @foo
          {dir1.as_posix()}
          {dir2.as_posix()}
          {dir3.as_posix()}
        """,
    )
    tags.execute(["--r", "--json"])
    assert_stdout(
        capsys,
        f"""
        {{
          "{dir1.name}": [
            "{dir1.as_posix()}"
          ],
          "{dir2.name}": [
            "{dir2.as_posix()}"
          ],
          "{dir3.name}": [
            "{dir3.as_posix()}"
          ],
          "foo": [
            "{dir1.as_posix()}",
            "{dir2.as_posix()}",
            "{dir3.as_posix()}"
          ]
        }}
        """,
    )
    tags.execute(["-y", "--purge"])
    assert_stdout(
        capsys,
        f"""
        {dir1.as_posix()} -@{dir1.name} -@foo
        {dir2.as_posix()} -@{dir2.name} -@foo
        {dir3.as_posix()} -@{dir3.name} -@foo
        Tags purged successfully
        """,
    )
    assert load_completion() == []
    tags.execute(["-p"])
    assert_stdout(
        capsys,
        "Nothing to purge",
    )
    tag.execute([dir3.as_posix(), dir2.as_posix(), dir1.as_posix(), "-y", "-t", "foo"])
    assert_stdout(
        capsys,
        f"""
        {dir1.as_posix()} +@foo
        {dir2.as_posix()} +@foo
        {dir3.as_posix()} +@foo
        Tags saved successfully
        """,
    )
    shutil.rmtree(dir1, ignore_errors=True)
    shutil.rmtree(dir2, ignore_errors=True)
    tags.execute(["--yes", "--clean"])
    assert_stdout(
        capsys,
        f"""
        {dir1.as_posix()} -@foo
        {dir2.as_posix()} -@foo
        Tags cleaned successfully
        """,
    )
    assert load_completion() == ["foo"]
    tags.execute(["--clean"])
    assert_stdout(
        capsys,
        "Nothing to clean",
    )
