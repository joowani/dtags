# dtags 
Directory tags for lazy programmers.
Inspired by [gr](https://github.com/mixu/gr).

#### Introduction

Do you have too many git repositories or vagrant machines to manage? Does your 
daily workflow require you to switch between directories more often than you 
would like? Do you constantly look for ways to type less for more? If you 
answered *yes* to any of these questions, then dtags may be for you!

#### Getting Started

Install using [pip](https://pip.pypa.io) (Python 2.7+ and 3.4+):
```bash
~$ sudo pip install --upgrade pip setuptools
~$ sudo pip install --upgrade dtags
```

Once installed, you have 4 commands at your disposal: 
`tags`, `tag`, `untag` and `run`.

Tag the directories (tag names must begin with `@`):
```bash
~$ tag /home/joowani/frontend @frontend
~$ tag /home/joowani/backend @backend
~$ tag ~/frontend ~/backend @work
~$ tag ~/db @vm
~$ tag ~/web @vm
# Or equivalently
~$ tag ~/frontend @frontend @work ~/backend @backend @work ~/db ~/web @vm
```

You can then run commands in the tagged directories:
```bash
~$ run @project git fetch origin
~$ run @frontend @backend git status -sb
~$ run @vms vagrant up
```

Directory paths can be used as well:
```bash
~$ run @backend ~/scripts ~/redis ls -la
```

Run commands in parallel with `-p` and display exit codes with `-e`:
```bash
# When running things in parallel ensure your command doesn't wait for input!
~$ run -p @backend 'sleep 5 && echo done'
~$ run -p @project git pull
~$ run -p @vms vagrant up
~$ run -e @project ls folder
```

Use the command `tags` to display or edit current tags:
```bash
~$ tags						 # display all tags defined
~$ tags @backend @frontend   # display only the specified tags
~$ tags --json               # display the raw JSON
~$ tags --expand             # expand home (~)
~$ tags --reverse            # show the reverse mapping
~$ tags --edit               # edit the JSON directly using an editor
```

Export and reuse your tags with `tags --json`:
```bash
~$ tags --json @foo @bar | ssh user@host "cat > ~/.dtags"
```

Remove the tags you don't need anymore:
```bash
~$ untag ~/frontend @frontend ~/backend @backend
~$ untag /vagrant/web /vagrant/db @vms
~$ untag --all @backend   # removes the tag completely
~$ untag --all ~/vms/web  # removes the directory path from all tags
```

Last but not least, use the `--help` option to find out more!


#### Auto-completion

Auto-completion for **zsh** and **bash** are supported. I *strongly* recommend 
you to enable it (so you won't have to type the `@` symbol all the time).

If you use **bash**, place the following lines in your **~/.bashrc** 
(or **~/.bash_profile** for OS X):
```bash
if command -v register-python-argcomplete > /dev/null 2>&1; then
    eval "$(register-python-argcomplete run)"                                                                                                        
    eval "$(register-python-argcomplete tags)"
fi
```

If you use **zsh**, place the following lines in your **~/.zshrc**: 
```bash                                                                                  
autoload bashcompinit                                                           
bashcompinit 
if command -v register-python-argcomplete > /dev/null 2>&1; then
    eval "$(register-python-argcomplete run)"                                                                                                      
    eval "$(register-python-argcomplete tags)"
fi
```

#### To Do

* Warn the user when commands that are known to wait are run with `-p`
* Allow the user to customize the message header style & color
* Add options to `run` command for suppressing stdout and headers
* Add tests