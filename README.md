# DTags 
Directory tags for lazy programmers.
Written in Python, inspired by [gr](https://github.com/mixu/gr).

## Introduction

Do you have too many git repositories or vagrant machines to manage? Does your 
daily workflow require you to switch between different directories more often
than you would like? Are you always searching for ways to type your keyboard 
less? If your answered *yes* to any of these questions, then dtags may be for
you!

## Getting Started

Install using [pip](https://pip.pypa.io) (Python 2.7+ and 3.4+ supported):
```python
sudo pip install --upgrade pip setuptools
sudo pip install --upgrade dtags
```

Once installed, 4 commands will be available to you: 
`tags`, `tag`, `untag` and `run`.

Tag any number of directories to run commands in them at the same time without 
ever having to `cd`. For example, tag the directories you visit frequently:
```bash
> tag ~/frontend ~/backend ~/tools ~/scripts @project
> tag ~/vms/web ~/vms/db ~/vms/api @vms
```

Then you can run commands like this:
```bash
> run @project git status -sb
> run @vms vagrant up
> run @frontend ls -la
```

You can even run the commands in parallel:
```bash
> run -p @project git pull
> run -p @vms vagrant up
> run -p @backend 'sleep 5 && echo done'
```

If you want an overview of all your tags, you can use the command `tags` to
display them in a variety of ways:
```bash
> tags @backend @frontend   # filter by tags 
> tags --json               # display the raw JSON
> tags --expand             # expand home
> tags --reverse            # show the reverse mapping
```
You can also use the `--edit` option to edit the configuration file directly.



With the `--json` option you can export your dtags config in a flexible manner:
```bash
> tags --json @only @the @ones @your @friend @needs > export_file
```
You can then place the export file in `~/.dtags` for any other users or hosts to reuse the tags!

To remove the tags you don't need anymore:
```bash
> untag ~/frontend ~/backend ~/tools ~/scripts @project ~/backend @backend
> untag ~/vms/web ~/vms/db ~/vms/api @vms ~/has/many/tags @foo @bar
> untag --all @backend   # removes the tag completely
> untag --all ~/vms/web  # removes the path from all tags
```

If you need more help you can always use the `--help` option for any of the 
above commands.


## Auto-completion

Auto-completion for **zsh** and **bash** are supported. I *strongly* recommend 
you to enable it (so you don't have to type the `@` symbol all the time).

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
