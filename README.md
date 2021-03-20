# Dtags: Directory Tags for Lazy Programmers

[![Build](https://github.com/joowani/dtags/actions/workflows/build.yaml/badge.svg)](https://github.com/joowani/dtags/actions/workflows/build.yaml)
[![CodeQL](https://github.com/joowani/dtags/actions/workflows/codeql.yaml/badge.svg)](https://github.com/joowani/dtags/actions/workflows/codeql.yaml)
[![codecov](https://codecov.io/gh/joowani/dtags/branch/main/graph/badge.svg?token=znq5L1yeSz)](https://codecov.io/gh/joowani/dtags)
[![PyPI version](https://badge.fury.io/py/dtags.svg)](https://badge.fury.io/py/dtags)
[![GitHub license](https://img.shields.io/github/license/joowani/dtags?color=brightgreen)](https://github.com/joowani/dtags/blob/main/LICENSE)
![Python version](https://img.shields.io/badge/python-3.6%2B-blue)

**Dtags** is a command-line tool that lets you tag directories for 
faster filesystem navigation and command execution.

![Demo GIF](https://user-images.githubusercontent.com/2701938/111886599-1f63e800-898c-11eb-96e4-189af3401316.gif)

## Requirements

* Recent versions of Bash, Zsh or Fish
* Python 3.6+

## Installation

Install via [pip](https://pip.pypa.io):

```shell
pip install dtags
```

For Bash, add the following line in `~/.bashrc`:
```shell
source <(dtags-activate bash)
```

For Zsh, add the following line in `~/.zshrc`:
```shell
source <(dtags-activate zsh)
```

For Fish, add the following line in `~/.config/fish/config.fish`:
```shell
dtags-activate fish | source
```

For [Git Bash on Windows](https://git-scm.com/download/win), add the following lines 
in `~/.bashrc`:
```shell
export DTAGS_GIT_BASH=1
source <(dtags-activate bash)
```

Restart your shell. The following commands will be available after:
```shell
tag --help
untag --help
tags --help
d --help
run --help
```
Tab-completion should work out-of-the-box.

## Usage

Tag directories with `tag`:
```shell
# Tag directory ~/foo with "work" (tags are indicated with the "@" prefix)
$ tag ~/foo -t work
/home/user/foo +@work

# If tag names are not specified, directory basenames are used instead
$ tag ~/foo
/home/user/foo +@foo

# Tag directories ~/bar and ~/baz with "app" and "work" (many-to-many)
$ tag ~/bar ~/baz -t app work
/home/user/bar +@app +@work
/home/user/baz +@app +@work
```
Execute commands in one or more directories with `run`:
```shell
# Run "git status" in all directories tagged "work"
$ run work -c git status

# Run "git status" in directories ~/foo and ~/bar
$ run ~/foo ~/bar -c git status

# Mix tags and directory paths
$ run work ~/foo -c git status
```
Change directories by path or tag with `d`:
```shell
# Go to directory tagged "work" 
# If there are multiple directories, a selection prompt is displayed
$ d work

# Go to directory ~/foo (works just like cd)
$ d ~/foo

# Use -t/--tag to always assume the argument is a tag
$ d -t foo
```
Untag directories with `untag`:
```shell
# Remove tags "app" and "work" from directory ~/foo and ~/bar
$ untag ~/foo ~/bar -t app work

# Remove all tags from directory ~/foo
$ untag ~/foo

# Remove tag "app" from all directories
$ untag -t app
```
Manage tags with `tags`:
```shell
# List all tags
$ tags

# List all tags in JSON format
$ tags --json

# Clean invalid directories
$ tags --clean

# Remove all tags
$ tags --purge
```
Use `--help` to see more information on each command.

## Technical Notes
* Tags are saved in `~/.dtags` directory (created when a dtags command is first run). 
* The files in `~/.dtags` are not meant to be edited manually.
* By default, directory paths take precedence over tags when name collisions occur.
* Tag names are automatically slugified (e.g. "foo bar" to "foo-bar"). 
* Tag names are displayed with the "@" character prefix for easy identification.
* Directory paths and tag names are ordered alphabetically.

## Uninstallation

Run the following commands to completely uninstall dtags:

```shell
$ pip uninstall dtags
$ rm -rf ~/.dtags
```

Then remove the `dtags-activate` line from your shell runtime configuration.
