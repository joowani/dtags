# dtags 
Directory tags for lazy programmers.
Inspired by [gr](https://github.com/mixu/gr).

#### Introduction

Do you have too many git repositories or vagrant machines to manage? Does your 
daily routine require you to switch between the same directories over and over? 
Are you a lazy programmer who is always looking for shortcuts? If you answered
*yes* to any of these questions, then **dtags** may be for you!

#### Installation

Install using [pip](https://pip.pypa.io) (Python 2.7+ and 3.4+ supported):
```bash
~$ sudo pip install --upgrade pip setuptools
~$ sudo pip install --upgrade dtags
```

To get the latest commits:
```bash
~$ git clone https://github.com/joowani/dtags.git
~$ cd dtags
~$ sudo python setup.py install
```

Once installed, you will have 4 commands at your disposal: 
`tag`, `run`, `tags` and `untag`. 

#### Usage

Tag directories using `tag`:
```bash
~$ tag ~/frontend @frontend
~$ tag ~/backend @backend
~$ tag ~/frontend ~/backend @work
~$ tag ~/db @vm
~$ tag ~/web @vm

# Or equivalently
~$ tag ~/frontend @frontend @work ~/backend @backend @work ~/db ~/web @vm

# Note: All tag names must begin with the '@' symbol
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

# Display exit codes for each execution
~$ run -e @backend ls foobar

# Commands are executed through interactive shells so you can use your aliases!
~$ run @project myalias
```

Display/edit tags using `tags`:
```bash
~$ tags						 # display all tags
~$ tags @backend @frontend   # display only the specified tags
~$ tags --json               # display the raw JSON
~$ tags --expand             # expand home (~)
~$ tags --reverse            # show the reverse mapping
~$ tags --edit               # edit the JSON directly using an editor
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

You can always use the `--help` option to find out more!

#### Auto-completion

Auto-completion for **zsh** and **bash** are supported. I recommend you to 
enable it so you won't have to type the `@` symbol all the time.

For bash, place the following lines (or something similar) in your 
**~/.bashrc** (**~/.bash_profile** for OS X):
```bash
if command -v register-python-argcomplete > /dev/null 2>&1; then
    eval "$(register-python-argcomplete run)"                                                                                                        
    eval "$(register-python-argcomplete tags)"
fi
```

For zsh, place the following lines (or something similar) in your **~/.zshrc**: 
```bash                                                                                  
autoload bashcompinit                                                           
bashcompinit 
if command -v register-python-argcomplete > /dev/null 2>&1; then
    eval "$(register-python-argcomplete run)"                                                                                                      
    eval "$(register-python-argcomplete tags)"
fi
```

#### Notes

* dtags is not supported on Windows
* `run -p` will probably hang on interactive commands that wait on input
* `run -p` may use up a lot of memory on commands that produce large output
* `run -p` sends *sigterm* to its child processes when interrupted.

#### To Do

* Extension support
* Improve the configuration to include things other than just tags
* Warn the user when commands known to hang are executed with `run -p`
* Add integration tests
