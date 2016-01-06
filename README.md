# dtags 
Directory tags for lazy programmers.
Written in Python, heavily inspired by [gr](https://github.com/mixu/gr)

## Introduction

Do you have a lot of [git](https://git-scm.com/) repositories or 
[vagrant](https://www.vagrantup.com/) machines to manage? Does your daily workflow 
require you to switch between directories all the time? Are you a lazy programmer? 
If your answered *yes* to any of these questions, then dtags may be for you!

You can use dtags to tag any number of paths and run commands in them without ever
having to change directories. For example, you can tag a bunch of locations you 
visit frequently like this:
```bash
tag ~/frontend ~/backend ~/tools ~/scripts @work
tag ~/vms/web ~/vms/db ~/vms/api @vms 
```

Than do something cool like this:
```bash
run @work git status
run @vms vagrant up
run @work @vms ls -la
```

## Installation

Install using [pip](https://pip.pypa.io) (supports version 2.7+ and 3.4+):
```python
sudo pip install --upgrade pip setuptools
sudo pip install --upgrade dtags
```

Once installed, 4 commands will be available to you: 
**tags**, **tag**, **untag** and **run**.

## Usage

Here are some ways I use dtags:

```bash
tag ~/frontend @frontend @work ~/backend @backend @work ~/tools @tools @work ~/scripts @scripts

run @frontend @tools git pull
run @backend git checkout stage
run @backend git checkout 

```

## Auto-completion

dtags supports tab completion for zsh and bash.
I *strongly* recommend you to enable it.

If you use **bash**, place the following lines in your **~/.bashrc** (or **~/.bash_profile** for OS X):
```bash
eval "$(register-python-argcomplete run)"                                                                                                        
eval "$(register-python-argcomplete tags)"                                        
```

If you use **zsh**, place the following lines in your **~/.zshrc**: 
```bash
# Enable bash autocompletion                                                                                  
autoload bashcompinit                                                           
bashcompinit 
eval "$(register-python-argcomplete run)"                                                                                                      
eval "$(register-python-argcomplete tags)"                                      
```