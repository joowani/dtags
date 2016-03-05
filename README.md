# DTags - Directory Tags for Lazy Programmers. 

## Introduction

Do you have too many git repositories or vagrant machines to manage? Does your 
work require you to switch between the same directories over and over? Are you 
a lazy programmer who is always looking for shortcuts? If you answered *yes* to
any of these questions, then **dtags** may be for you!

## Features

**dtags** is a lightweight command line tool which lets you:

* Tag and un-tag directories
* Change directories quickly using the tag names
* Automate command executions in multiple directories

The goal is to save the user as many keystrokes as possible while maintaining 
clarity, flexibility and usability. 

All commands come with tab-completion.

## Installation

**Step 1**: Check requirements

* Python 2.7+ or 3.4+ 
* Recent version of [pip](https://pip.pypa.io) 
* Recent version of Bash, Zsh or Fish with tab-completion enabled

**Step 2**: Install the package:
```bash
# You may need to sudo depending on your setup
~$ pip install --upgrade dtags
```

**Step 3**: Modify your shell runtime configuration:
```bash
# For zsh, place in ~/.zshrc:
command -v dtags > /dev/null 2>&1 && . <(dtags shell zsh)

# For bash, place in ~/.bashrc (or ~/.bash_profile for OS X):
command -v dtags > /dev/null 2>&1 && . <(dtags shell bash)

# For fish, place in ~/.config/fish/config.fish:
command -v dtags > /dev/null 2>&1; and dtags shell fish | source
```

**Step 4**. Restart your shell.

    Note for those are already using v1.x.x:
      dtags v2 has config changes that are not backwards-compatible.
      If you want to upgrade from v1, you need to run a migration script:
      
       ~$ git clone https://github.com/joowani/dtags.git
       ~$ python dtags/scripts/migrate.py
       
      If you don't mind losing your tags, simply run 'rm -rf ~/.dtags' instead.


Once installed, you will have **5** commands at your disposal: `tag`, `untag`, 
`d`, `e` and `dtags`.

## Usage Examples

Tag directories with `tag`:
```bash
~$ tag ~/web dev work   # add tags 'dev' and 'work' to ~/web
~$ tag ~/app            # tag ~/app with its basename, 'app'
```

Un-tag directories with `untag`:
```bash
~$ untag ~/web dev      # remove tag 'dev' from ~/web
~$ untag ~/app          # remove all tags from ~/app 
```

Change directories with `d` (designed to fully replace `cd`!):
```bash
~$ d                    # go to the user's home directory 
~$ d frontend           # go to the directory tagged 'frontend'
~$ d tag_with_many_dirs # prompt the user to select a specific directory         
~$ d ~/app              # go to directory ~/app
```

Execute commands in one or more directories with `e`:
```bash
~$ e repo git status    # execute 'git status' in directories tagged 'repo'
~$ e ~/vm vagrant halt  # execute 'vagrant halt' in directory ~/vm
~$ e -p vm git pull     # execute 'git pull' in directories tagged 'vm' in parallel
~$ e vm,~/foo ls        # execute 'ls' in directories tagged 'vm' and ~/foo
```

Search and manage tags with `dtags`:
```bash
~$ dtags list		    # display directories-to-tags mapping
~$ dtags list ~/app     # display the tags and directories associated with ~/app
~$ dtags list foo bar   # display the tags and directories associated with 'foo' or 'bar'
~$ dtags reverse        # display tags-to-directories mapping
~$ dtags edit           # edit tags and directories via editor like vim
~$ dtags clean          # remove invalid or stale tags and directories
```

You can always use the `--help` option to find out more!

## Technical Notes

* Windows is currently not supported
* `e -p` hangs on interactive commands that wait on input
* `e -p` sends *sigterm* to its child processes when killed
* `e` is affected by shell startup times (beware *oh-my-zsh* users)
* `e` uses environment variable $SHELL to guess which shell is in use
* `dtags edit` uses environment variable $EDITOR
