# DTags 
Directory tags for lazy programmers.
Written in Python, inspired by [gr](https://github.com/mixu/gr)

## Introduction

Do you have too many git repositories or vagrant machines to manage? Does your 
daily workflow require you to switch between directories often? Are you always 
looking for ways to type less? If your answered yes to any of these questions, 
then dtags may be for you!

## Getting Started

Install using [pip](https://pip.pypa.io) (Python 2.7+ and 3.4+ supported):
```python
sudo pip install --upgrade pip setuptools
sudo pip install --upgrade dtags
```

Once installed, 4 commands will be available to you: 
**tags**, **tag**, **untag** and **run**.

You can tag any number of directories and run commands in them without ever
having to `cd`. For example, tag the directories you visit frequently:
```bash
> tag ~/frontend ~/backend ~/tools ~/scripts @project
> tag ~/vms/web ~/vms/db ~/vms/api @vms
```

Then you can do run commands like this:
```bash
> run @project git status -sb
> run @vms vagrant up
```

You can even run the commands in parallel (but you lose font colors):
```bash
> run -p @project git status -sb
> run -p @vms vagrant up
```

If you want an overview of all your tags, you can run the command `tags` to
display them in a variety of ways:
```bash
> tags @backend @frontend   # filter by tags 
> tags --json               # display in json
> tags --expand             # expand user home
> tags --reverse            # show the reverse mapping
```

Lastly, to remove tags you don't need anymore:
```bash
> untag ~/frontend ~/backend ~/tools ~/scripts @project ~/backend @backend
> untag ~/vms/web ~/vms/db ~/vms/api @vms ~/has/many/tags @foo @bar
```

If you need more help you can always use the option `--help`.


## Auto-completion

Auto-completion for **zsh** and **bash** are supported. I *strongly* recommend 
you to enable it so you don't have to type the `@` symbols all the time.

If you use **bash**, place the following lines in your **~/.bashrc** 
(or **~/.bash_profile** for OS X):
```bash
eval "$(register-python-argcomplete run)"                                                                                                        
eval "$(register-python-argcomplete tags)"                                        
```

If you use **zsh**, place the following lines in your **~/.zshrc**: 
```bash                                                                                  
autoload bashcompinit                                                           
bashcompinit 
eval "$(register-python-argcomplete run)"                                                                                                      
eval "$(register-python-argcomplete tags)"                                      
```