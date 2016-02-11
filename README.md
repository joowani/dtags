# dtags 
Directory tags for lazy programmers. 

#### Introduction

Do you have too many git repositories or vagrant machines to manage? Does your 
daily routine require you to switch between the same directories over and over? 
Are you a lazy programmer who is always looking for shortcuts? If you answered
*yes* to any of these questions, then **dtags** may be for you!

#### Features

**dtags** is a small command line tool which lets you:

* Tag and un-tag directories
* Change directories quickly via tags (similar to aliases easier to manage)
* Execute commands in multiple directories at once

The goal of **dtags** is to save the user as many keystrokes as possible while
being flexible and easy to use.

#### Announcements

dtags **v2.x** has configuration changes that are not backwards-compatible. 
If you want to upgrade from **v1.x** while retaining your tags, you will need 
to run the migration script *before* you upgrade:
```bash
~$ git clone https://github.com/joowani/dtags.git
~$ python dtags/scripts/migrate.py
```

#### Installation

Requirements:
* Python 2.7+ or 3.4+
* Bash, Zsh or Fish (recent versions recommended)

Install using [pip](https://pip.pypa.io) 
(dtags respects [virtualenv](https://virtualenv.readthedocs.org)):
```bash
~$ pip install dtags
```

If you use `zsh` or `bash`, place the following in your `.bashrc` 
(`.bash_profile` on OSX) or `.zshrc`:

```command -v dtags > /dev/null 2>&1 && . <(dtags shell)```

If you use `fish`, place the following in your `~/.config/fish/config.fish`:

```command -v dtags > /dev/null 2>&1; and dtags shell | source;```

Once installed, you will have 5 commands at your disposal: 
`tag`, `untag`, `d`, `e` and `dtags`

Please ensure you don't have any aliases with the same names.

#### Usage Examples

Tag or un-tag directories with commands `tag` and `untag`:
```bash
# Usage: tag <dir> [<tag>...]
~$ tag /home/app            # add tag 'app' to /home/app
~$ tag /home/web dev work   # add tags 'dev' and 'work' to /home/web
```
```bash
# Usage: untag <dir> [<tag>...]
~$ untag /home/web dev      # remove tag 'dev' from /home/web
~$ untag /home/app          # remove all tags from /home/app 
```

Change directories quickly with command `d` (meant to replace `cd`):
```bash
# Usage: d [<tag>|<dir>]
~$ d                        # go to the home directory 
~$ d frontend               # go to the directory tagged 'frontend'
~$ d ~/home/app             # go to directory ~/home/app 
```

Execute commands in the directories with command `e`:
```bash
# Usage: e [-p] <targets> <command> [<arg>...]
~$ e app ls                 # execute 'ls' in directories tagged 'app'
~$ e vm vagrant up          # execute 'vagrant up' in directories tagged 'vm'
~$ e repo git pull          # execute 'git pull' in parallel
```

Manage the tags with command `dtags`:
```bash
~$ dtags				    # show the directories-to-tags mapping
~$ dtags list ~             # show all tags mapped to the home directory
~$ dtags list foo bar       # show all directories with tags 'foo' or 'bar'
~$ dtags reverse            # show the tags-to-directories mapping
~$ dtags edit               # edit tags and directories using an editor
~$ dtags clean              # remove stale directory paths and tags
```

You can always use the `--help` option to find out more!

#### Notes

* Windows is not supported yet
* `e -p` hangs on interactive commands that wait on input (e.g. vim)
* `e -p` sends *sigterm* to its child processes when killed
* `e` can be slowed down by shell startup (e.g. oh-my-zsh)
* `e` decides which shell you are using with the environment variable $SHELL
