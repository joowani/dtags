# dtags 
Directory tags for lazy programmers.
Inspired by [gr](https://github.com/mixu/gr).

#### Introduction

Do you have too many git repositories or vagrant machines to manage? Do your 
daily tasks require you to switch between the same directories over and over? 
Are you lazy programmer who's always looking for shortcuts? If you answered
*yes* to any of these questions, then dtags may be for you!

#### Getting Started

Install using [pip](https://pip.pypa.io) (Python 2.7+ and 3.4+):
```bash
~$ sudo pip install --upgrade pip setuptools
~$ sudo pip install --upgrade dtags
```

Once installed, you will have 4 commands at your disposal: 
`tags`, `tag`, `untag` and `run`.

Tag directories using `tag`:
```bash
~$ tag ~/frontend @frontend
~$ tag ~/backend @backend
~$ tag ~/frontend ~/backend @work
~$ tag ~/db @vm
~$ tag ~/web @vm

# Or equivalently:
~$ tag ~/frontend @frontend @work ~/backend @backend @work ~/db ~/web @vm

# All tag names must begin with the @ symbol
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

# The commands can be executed in parallel as long as it doesn't wait for input!
~$ run -p @backend 'sleep 5 && echo done'
~$ run -p @project git pull
~$ run -p @vms vagrant up
```

Display/edit tags using `tags`:
```bash
~$ tags						 # display all tags defined
~$ tags @backend @frontend   # display only the specified tags
~$ tags --json               # display the raw JSON
~$ tags --expand             # expand home (~)
~$ tags --reverse            # show the reverse mapping
~$ tags --edit               # edit the JSON directly using an editor
```

Disassociate tags and directory paths using `untag`:
```bash

# Remove tags @frontend and @backend from directories ~/frontend and ~/backend respectively
~$ untag ~/frontend @frontend ~/backend @backend

# Remove tags @vms from directories /vagrant/web and /vagrant/db
~$ untag /vagrant/web /vagrant/db @vms

# Remove tag @backend completely
~$ untag --all @backend

# Remove the directory path ~/vms/web from all tags
~$ untag --all ~/vms/web 
```

You can always use the `--help` option to find out more!


#### Auto-completion

Auto-completion for **zsh** and **bash** are supported. I recommend you to 
enable it if possible so you won't have to type the `@` symbol all the time.

For bash, place the following lines or something similar in your 
**~/.bashrc** (**~/.bash_profile** for OS X):
```bash
if command -v register-python-argcomplete > /dev/null 2>&1; then
    eval "$(register-python-argcomplete run)"                                                                                                        
    eval "$(register-python-argcomplete tags)"
fi
```

For zsh, place the following lines pr something similar in your **~/.zshrc**: 
```bash                                                                                  
autoload bashcompinit                                                           
bashcompinit 
if command -v register-python-argcomplete > /dev/null 2>&1; then
    eval "$(register-python-argcomplete run)"                                                                                                      
    eval "$(register-python-argcomplete tags)"
fi
```

#### To Do

* Warn the user when commands known to hang are executed with `run -p`
* Allow the user to customize the message header style and color
* Add options to `run` command for suppressing stdout and headers
* Add tests
