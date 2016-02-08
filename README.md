# dtags 
Directory tags for lazy programmers. 
Inspired by [gr](https://github.com/mixu/gr).

Please refer to the [release notes](https://github.com/joowani/dtags/releases) 
for details on other API changes.

#### Introduction

Do you have too many git repositories or vagrant machines to manage? Does your 
daily routine require you to go through the same directories over and over? 
Are you a lazy programmer who is always looking for shortcuts? If you answered
*yes* to any of these questions, then **dtags** may be for you!

#### Announcements

dtags v1.1.0 includes a config change which breaks backwards-compatibility (but 
the change is for the better... I promise). So if you are using v1.0.9 or below
and want to upgrade to the latest version while retaining your tags, you will 
need to follow these steps first:
```bash
~$ git clone https://github.com/joowani/dtags.git
~$ python dtags/scripts/migrate.py
# Now you can run upgrade to the newer version
```

#### Installation

Requirements:
* Python 2.7+ or 3.4+
* Bash 4+ or Zsh 5+

Install using [pip](https://pip.pypa.io) 
(respects [virtualenv](https://virtualenv.readthedocs.org)):
```bash
# You may need to use sudo depending on your setup
~$ pip install --upgrade pip setuptools
~$ pip install --upgrade dtags
```

Place the following lines (or similar) in your `.bashrc` or `.zshrc`
```bash
autoload bashcompinit && bashcompinit  # needed for zsh auto-completion only
if command -v dtags-rc > /dev/null 2>&1; then . <(dtags-rc); fi
```

Once installed, you will have 5 commands at your disposal: 
`tag`, `untag`, `run`, `tags` and `goto`. 

#### Usage & Examples

Tag directories using `tag`:
```bash
~$ tag ~/frontend @frontend
~$ tag ~/backend @backend
~$ tag ~/frontend ~/backend @work
~$ tag ~/db @vm
~$ tag ~/web @vm

# Or equivalently
~$ tag ~/frontend @frontend @work ~/backend @backend @work ~/db ~/web @vm

# All tag names must begin with the '@' symbol
```

Execute commands in the tagged directories using `run`:
```bash
# Execute 'git fetch origin' in all directories tagged @project
~$ run @project git fetch origin

# Execute 'git status -sb' in all directories tagged @frontend and @backend
~$ run @frontend @backend git status -sb

# Execute 'vagrant status' in all directories tagged @vms
~$ run @vms vagrant status

# Directory paths can be specified along with tags
~$ run @backend ~/scripts ~/redis ls -la

# The command can be executed in parallel if it doesn't wait on input
~$ run -p @backend 'sleep 5 && echo done'
~$ run -p @project git pull
~$ run -p @vms vagrant up

# Display the exit code for each execution
~$ run -e @backend ls foobar

# Execute the command in interactive mode to use aliases and functions
~$ run -i @project 'myalias && myfunc'
```

Display/edit tags using `tags`:
```bash
~$ tags						    # show all tags
~$ tags ~/foobar                # show only the tags with the specified path
~$ tags @backend @frontend      # show only the specified tags
~$ tags --user                  # expand user (~)
~$ tags --reverse               # show the reverse mapping
~$ tags --edit                  # edit the tags directly using an editor
~$ tags --clean                 # remove stale directory paths and tags
```

Disassociate tags and directory paths using `untag`:
```bash
# Remove tags @frontend and @backend from ~/frontend and ~/backend respectively
~$ untag ~/frontend @frontend ~/backend @backend

# Remove tags @vms from directories /vagrant/web and /vagrant/db
~$ untag /vagrant/web /vagrant/db @vms

# Remove the tag @backend completely
~$ untag --all @backend

# Remove the directory path ~/vms/web from all tags
~$ untag --all ~/vms/web 
```

Quickly `cd` to the tagged directories using `goto`:
```bash
# If there is a 1-to-1 mapping between the directory and the tag, cd right away
~/old$ goto @new  # or you can omit the '@' symbol and do 'goto new'
~/new$

# If multiple directories are mapped to the tag, prompt for selection then cd
~/old$ goto @multiple  # or 'goto multiple'
1: ~/foo
2: ~/bar
3: ~/baz

Select directory (1-3): 2
~/bar$
```
You can always use the `--help` option to find out more!

#### Notes

* dtags is _not_ supported on Windows
* `run -p` hangs on interactive commands that wait on input (e.g. vim)
* `run -p` dumps the entire output of the commands into memory
* `run -p` sends *sigterm* to its child processes when killed
* `run -i` can be slow depending on the loading time of your shell

#### To Do

* Add Extension support
* Allow the user to customize the header messages for the `run` command
* Improve the configuration to include things other than just tags
* Warn the user when commands known to hang are executed with `run -p`
* Add tests
