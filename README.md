# DTags - Directory tags for lazy programmers. 

## Introduction

Do you have too many git repositories or vagrant machines to manage? Does your 
work require you to switch between the same directories over and over? Are you 
a lazy programmer who is always looking for shortcuts? If you answered *yes* to
any of the above questions, then **dtags** may be for you!

## Features

**dtags** is a lightweight command line tool which lets you:

* Tag and un-tag directories
* Change directories quickly by tag name
* Automate command executions in multiple directories

The goal is to save the user as many keystrokes as possible while 
maintaining clarity, flexibility and usability.

## Installation

**Step 1**: Check requirements

* Python 2.7+ or 3.4+
* Bash, Zsh or Fish with tab-completion enabled

**Step 2**: Install using [pip](https://pip.pypa.io) 
(respects [virtualenv](https://virtualenv.readthedocs.org)):
```bash
~$ pip install dtags
```

**Step 3**: Place the following line in your shell runtime config:
```bash
# For zsh, place in ~/.zshrc:
command -v dtags > /dev/null 2>&1 && . <(dtags shell zsh)

# For bash, place in ~/.bashrc (or ~/.bash_profile for OSX):
command -v dtags > /dev/null 2>&1 && . <(dtags shell bash)

# For fish, place in ~/.config/fish/config.fish:
command -v dtags > /dev/null 2>&1; and dtags shell fish | source
```

**Step 4**. Restart your shell.


For v1 users:
   * dtags v2 has config changes that are *not* backwards-compatible
   * If you want to upgrade from v1, you need to run the migration script:
      
      ```bash
       ~$ git clone https://github.com/joowani/dtags.git
       ~$ python dtags/scripts/migrate.py
       ```
       
   * Or if you don't mind losing your tags, simply run `rm -rf ~/.dtags`.


Once installed, you will have 5 commands at your disposal: `tag`, `untag`, 
`d`, `e` and `dtags` (make sure that you don't have any aliases with the same 
names).

## Usage Examples

Tag directories with `tag`:
```bash
# Usage: tag <dir> [<tag>...]

~$ tag ~/app            # add tag 'app' to ~/app
~$ tag ~/web dev work   # add tags 'dev' and 'work' to ~/web
```

Un-tag directories with `untag`:
```bash
# Usage: untag <dir> [<tag>...]

~$ untag ~/web dev      # remove tag 'dev' from ~/web
~$ untag ~/app          # remove all tags from ~/app 
```

Change directories with `d` (meant to fully replace `cd`!):
```bash
# Usage: d [<tag>|<dir>]

~$ d                    # go to the user's home directory 
~$ d frontend           # go to the directory tagged 'frontend'
~$ d many_dirs          # prompt the user to select the destination         
~$ d ~/app              # go to ~/app
```

Execute commands in the directories with `e`:
```bash
# Usage: e [-p] <targets> <command> [<arg>...]

~$ e app ls             # execute 'ls' in directories tagged 'app'
~$ e vm vagrant up      # execute 'vagrant up' in directories tagged 'vm'
~$ e repo git pull      # execute 'git pull' in parallel
```

Display and manage tags with `dtags` (I like to have this aliased to `tags`):
```bash
~$ dtags				# display directories-to-tags mapping
~$ dtags list ~         # display all tags mapped to the home directory
~$ dtags list foo bar   # display all directories with tags 'foo' or 'bar'
~$ dtags reverse        # display tags-to-directories mapping
~$ dtags edit           # edit tags and directories via editor (e.g. vim)
~$ dtags clean          # remove invalid/stale tags and directories
```

You can always use the `--help` option to find out more!

## Notes

* Windows is currently not supported
* `e -p` hangs on interactive commands that wait on input (e.g. vim)
* `e -p` sends *sigterm* to its child processes when killed
* `e` can be slowed down by shell startup (e.g. oh-my-zsh)
* `e` decides which shell you are using with the environment variable $SHELL
