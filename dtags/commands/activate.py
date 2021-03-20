import sys
from typing import List, Optional

from dtags.commons import dtags_command, get_argparser

USAGE = "dtags-activate {bash,fish,zsh}"
DESCRIPTION = "Activate dtags"

BASH_ACTIVATE_SCRIPT = """
unalias tag > /dev/null 2>&1
unalias untag > /dev/null 2>&1
unalias tags > /dev/null 2>&1
unalias d > /dev/null 2>&1
unalias run > /dev/null 2>&1
d() {
    if [[ $# -eq 1 ]] && [[ -d $1 ]]
    then
        cd "${1}"
    elif [[ $# -eq 1 ]] && [[ $1 = - ]]
    then
        cd -
    else
        dtags-d "$@"
        if [[ -f ~/.dtags/destination ]]
        then
            cd "$(cat ~/.dtags/destination)"
            rm -f ~/.dtags/destination
        fi
    fi
}
_dtags_d() {
    declare CWORD="${COMP_WORDS[COMP_CWORD]}"
    if [[ -f ~/.dtags/completion ]]
    then
        COMPREPLY+=($(compgen -W "$(cat ~/.dtags/completion)" -- "${CWORD}"))
    fi
    if [[ ${COMP_CWORD} -eq 1 ]]
    then
        COMPREPLY+=($(compgen -W "-h --help -v --version -t --tag" -- "${CWORD}"))
    fi
}
_dtags_tag() {
    declare CWORD="${COMP_WORDS[COMP_CWORD]}"
    if [[ -f ~/.dtags/completion ]]
    then
        COMPREPLY+=($(compgen -W "$(cat ~/.dtags/completion)" -- "${CWORD}"))
    fi
    COMPREPLY+=($(compgen -W "-t -y --yes -r --replace" -- "${CWORD}"))
    if [[ ${COMP_CWORD} -eq 1 ]]
    then
        COMPREPLY+=($(compgen -W "-h --help -v --version" -- "${CWORD}"))
    fi
}
_dtags_untag() {
    declare CWORD="${COMP_WORDS[COMP_CWORD]}"
    if [[ -f ~/.dtags/completion ]]
    then
        COMPREPLY+=($(compgen -W "$(cat ~/.dtags/completion)" -- "${CWORD}"))
    fi
    COMPREPLY+=($(compgen -W "-t -y --yes" -- "${CWORD}"))
    if [[ ${COMP_CWORD} -eq 1 ]]
    then
        COMPREPLY+=($(compgen -W "-h --help -v --version" -- "${CWORD}"))
    fi
}
_dtags_tags() {
    declare CWORD="${COMP_WORDS[COMP_CWORD]}"
    if [[ -f ~/.dtags/completion ]]
    then
        COMPREPLY+=($(compgen -W "$(cat ~/.dtags/completion)" -- "${CWORD}"))
    fi
    COMPREPLY+=($(compgen -W "-j --json -r --reverse -y --yes" -- "${CWORD}"))
    COMPREPLY+=($(compgen -W "-c --clean -p --purge -t" -- "${CWORD}"))
    if [[ ${COMP_CWORD} -eq 1 ]]
    then
        COMPREPLY+=($(compgen -W "-h --help -v --version" -- "${CWORD}"))
    fi
}
_dtags_run() {
    declare CWORD="${COMP_WORDS[COMP_CWORD]}"
    if [[ -f ~/.dtags/completion ]]
    then
        COMPREPLY+=($(compgen -W "$(cat ~/.dtags/completion)" -- "${CWORD}"))
    fi
    COMPREPLY+=($(compgen -W "-c --cmd" -- "${CWORD}"))
    if [[ ${COMP_CWORD} -eq 1 ]]
    then
        COMPREPLY+=($(compgen -W "-h --help -v --version" -- "${CWORD}"))
    fi
}
complete -d -F _dtags_tag tag
complete -d -F _dtags_untag untag
complete -F _dtags_tags tags
complete -d -F _dtags_d d
complete -d -F _dtags_run run
"""

ZSH_ACTIVATE_SCRIPT = """
unalias tag > /dev/null 2>&1
unalias untag > /dev/null 2>&1
unalias tags > /dev/null 2>&1
unalias d > /dev/null 2>&1
unalias run > /dev/null 2>&1
d() {
    if [[ $# -eq 1 ]] && [[ -d $1 ]]
    then
        cd "${1}"
    elif [[ $# -eq 1 ]] && [[ $1 = - ]]
    then
        cd -
    else
        dtags-d "$@"
        if [[ -f ~/.dtags/destination ]]
        then
            cd "$(cat ~/.dtags/destination)"
            rm -f ~/.dtags/destination
        fi
    fi
}
_dtags_d() {
    _files -/
    if [[ -f ~/.dtags/completion ]]
    then
        compadd $(cat ~/.dtags/completion)
    fi
    if [[ CURRENT -eq 2 ]]
    then
        _arguments '-h' '--help' '-v' '--version' '-t' '--tag'
    fi
}
_dtags_tag() {
    _files -/
    if [[ -f ~/.dtags/completion ]]
    then
        compadd $(cat ~/.dtags/completion)
    fi
    _arguments '-t' '-y' '--yes' '-r' '--replace'
    if [[ CURRENT -eq 2 ]]
    then
        _arguments '-h' '--help' '-v' '--version'
    fi
}
_dtags_untag() {
    _files -/
    if [[ -f ~/.dtags/completion ]]
    then
        compadd $(cat ~/.dtags/completion)
    fi
    _arguments '-t' '-y' '--yes'
    if [[ CURRENT -eq 2 ]]
    then
        _arguments '-h' '--help' '-v' '--version'
    fi
}
_dtags_run() {
    _files -/
    if [[ -f ~/.dtags/completion ]]
    then
        compadd $(cat ~/.dtags/completion)
    fi
    _arguments '-c' '--cmd'
    if [[ CURRENT -eq 2 ]]
    then
        _arguments '-h' '--help' '-v' '--version'
    fi
}
_dtags_tags() {
    if [[ -f ~/.dtags/completion ]]
    then
        compadd $(cat ~/.dtags/completion)
    fi
    _arguments '-j' '--json' '-r' '--reverse' '-y' '--yes'
    _arguments '-c' '--clean' '-p' '--purge' '-t'
    if [[ CURRENT -eq 2 ]]
    then
        _arguments '-h' '--help' '-v' '--version'
    fi
}
compdef _dtags_tag tag
compdef _dtags_untag untag
compdef _dtags_tags tags
compdef _dtags_d d
compdef _dtags_run run
"""

FISH_ACTIVATE_SCRIPT = """
functions -e tag > /dev/null 2>&1
functions -e untag > /dev/null 2>&1
functions -e tags > /dev/null 2>&1
functions -e d > /dev/null 2>&1
functions -e run > /dev/null 2>&1

function d
    if [ (count $argv) -eq 1 ]
        if test -d $argv[1]
            cd $argv[1]
            return 0
        else if [ $argv[1] = "-" ]
            cd -
            return 0
        end
    end
    dtags-d $argv
    if test -f ~/.dtags/destination
        cd (cat ~/.dtags/destination)
        rm -f ~/.dtags/destination
    end
end

function __dtags_cond_no_args
    set cmd (commandline -opc)
    if [ (count $cmd) -eq 1 ]
        return 0
    else
        return 1
    end
end

function __dtags_complete_tags
    if test -f ~/.dtags/completion
        string split ' ' (cat ~/.dtags/completion)
    end
end

complete -c tag -a '(__dtags_complete_tags)' -d 'Tag'
complete -c tag -a '(__fish_complete_directories)'
complete -c tag -n '__dtags_cond_no_args' -s h -l help -d 'Flag'
complete -c tag -n '__dtags_cond_no_args' -s v -l version -d 'Flag'
complete -c tag -s t -d 'Flag'
complete -c tag -s y -l yes -d 'Flag'
complete -c tag -s r -l replace -d 'Flag'

complete -c untag -a '(__dtags_complete_tags)' -d 'Tag'
complete -c untag -a '(__fish_complete_directories)'
complete -c untag -n '__dtags_cond_no_args' -s h -l help -d 'Flag'
complete -c untag -n '__dtags_cond_no_args' -s v -l version -d 'Flag'
complete -c untag -s t -d 'Flag'
complete -c untag -s y -l yes -d 'Flag'

complete -c tags -a '(__dtags_complete_tags)' -d 'Tag'
complete -c tags -n '__dtags_cond_no_args' -s h -l help -d 'Flag'
complete -c tags -n '__dtags_cond_no_args' -s v -l version -d 'Flag'
complete -c tags -s t -d 'Flag'
complete -c tags -s j -l json -d 'Flag'
complete -c tags -s c -l clean -d 'Flag'
complete -c tags -s p -l purge -d 'Flag'
complete -c tags -s r -l reverse -d 'Flag'
complete -c tags -s y -l yes -d 'Flag'

complete -c d -a '(__dtags_complete_tags)' -d 'Tag'
complete -c d -a '(__fish_complete_directories)'
complete -c d -n '__dtags_cond_no_args' -s h -l help -d 'Flag'
complete -c d -n '__dtags_cond_no_args' -s v -l version -d 'Flag'
complete -c d -s t -l tag -d 'Flag'

complete -c run -a '(__dtags_complete_tags)' -d 'Tag'
complete -c run -a '(__fish_complete_directories)'
complete -c run -n '__dtags_cond_no_args' -s h -l help -d 'Flag'
complete -c run -n '__dtags_cond_no_args' -s v -l version -d 'Flag'
complete -c run -s c -l cmd -d 'Flag'
"""


@dtags_command
def execute(args: Optional[List[str]] = None) -> None:
    parser = get_argparser(
        prog="dtags-activate",
        desc=DESCRIPTION,
        usage=USAGE,
    )
    parser.add_argument(
        "shell",
        choices=["bash", "fish", "zsh"],
        help="Name of the shell",
    )
    parsed_args = parser.parse_args(sys.argv[1:] if args is None else args)

    if parsed_args.shell == "bash":
        print(BASH_ACTIVATE_SCRIPT)
    elif parsed_args.shell == "fish":
        print(FISH_ACTIVATE_SCRIPT)
    else:
        print(ZSH_ACTIVATE_SCRIPT)
