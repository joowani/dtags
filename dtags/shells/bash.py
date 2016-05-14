CONFIGURATION = """
unalias dtags > /dev/null 2>&1
unalias t > /dev/null 2>&1
unalias u > /dev/null 2>&1
unalias e > /dev/null 2>&1
unalias p > /dev/null 2>&1
unalias d > /dev/null 2>&1

function dtags() {{
    dtags-manage $@
    if [[ $1 = edit ]] || [[ $1 = clean ]]
    then
        eval "`dtags-refresh bash`"
    fi
}}

function t() {{
    dtags-t $@ && eval "`dtags-refresh bash`"
}}

function u() {{
    dtags-u $@ && eval "`dtags-refresh bash`"
}}

function d() {{
    declare _dtags_usage="{usage}"
    declare _dtags_version="{version}"
    declare _dtags_description="{description}"
    if [[ -t 1 ]]
    then
        declare _dtags_arg_err="{arg_err_tty}"
        declare _dtags_dest_err="{dest_err_tty}"
        declare _dtags_input_err="{input_err_tty}"
        declare _dtags_idx_err="{index_err_tty}"
        declare _dtags_prompt="{prompt_tty}"
        declare _dtags_choice="{choice_tty}"
    else
        declare _dtags_arg_err="{arg_err}"
        declare _dtags_dest_err="{dest_err}"
        declare _dtags_input_err="{input_err}"
        declare _dtags_idx_err="{index_err}"
        declare _dtags_prompt="{prompt}"
        declare _dtags_choice="{choice}"
    fi
    if [[ $# -lt 1 ]]
    then
        cd $HOME
        return 0
    elif [[ $1 = --help ]]
    then
        printf "$_dtags_usage$_dtags_description"
        return 0
    elif [[ $1 = --version ]]
    then
        printf "Version $_dtags_version\n"
        return 0
    elif [[ $1 = - ]]
    then
        cd "$OLDPWD"
        return 0
    elif [[ $1 = -* ]]
    then
        printf "$_dtags_arg_err" "$_dtags_usage" "$1"
        return 2
    elif [[ $# -gt 1 ]]
    then
        printf "%sd: too many arguments\n" "$_dtags_usage"
        return 2
    fi
    declare -a _dtags_dirs
    PREV_IFS=$IFS
    IFS=$'\n'
    _dtags_dirs=($(grep -F ,"$1", {mapping_file} | cut -d',' -f1))
    IFS=$PREV_IFS
    declare _dtags_count=${{#_dtags_dirs[@]}}
    if [[ $_dtags_count -eq 0 ]]
    then
        if [[ -d $1 ]]
        then
            declare _dtags_dir="$1"
        else
            printf "$_dtags_dest_err" "$1"
            return 2
        fi
    elif [[ $_dtags_count = 1 ]]
    then
        declare _dtags_dir=${{_dtags_dirs[0]}}
    else
        for i in `seq $_dtags_count`
        do
            printf "$_dtags_choice" "$i" "${{_dtags_dirs[$i-1]}}"
        done
        printf "$_dtags_prompt" "$_dtags_count"
        declare _dtags_idx=1
        read _dtags_idx
        if [[ ! $_dtags_idx =~ ^-?[0-9]+$ ]]
        then
            printf "$_dtags_input_err" "$_dtags_idx"
            return 2
        elif [[ $_dtags_idx -gt $_dtags_count ]] || [[ $_dtags_idx -lt 1 ]]
        then
            printf "$_dtags_idx_err" "$_dtags_idx"
            return 2
        fi
        declare _dtags_dir=${{_dtags_dirs[$_dtags_idx-1]}}
    fi
    if [[ -d $_dtags_dir ]]
    then
        cd "$_dtags_dir"
        return 0
    else
        printf "$_dtags_dest_err" "$_dtags_dir"
        return 2
    fi
}}

_dtags() {{
    declare cur=${{COMP_WORDS[COMP_CWORD]}}
    if [[ ${{COMP_CWORD}} -eq 1 ]]
    then
        COMPREPLY+=($(compgen -W "list reverse shell edit clean commands" -- $cur))
    elif [[ ${{COMP_WORDS[1]}} = list ]] || [[ ${{COMP_WORDS[1]}} = reverse ]]
    then
        if [[ -f "{tags_file}" ]]
        then
            COMPREPLY+=($(compgen -W "`cat {tags_file}`" -- $cur))
        fi
        _filedir -d
    fi
}}

_t() {{
    declare cur=${{COMP_WORDS[COMP_CWORD]}}
    if [[ ${{COMP_CWORD}} -eq 1 ]]
    then
        _filedir -d
    elif [[ -f "{tags_file}" ]] && [[ ! ${{COMP_WORDS[1]}} = -* ]]
    then
        COMPREPLY+=($(compgen -W "`cat {tags_file}`" -- $cur))
    fi
}}

_u() {{
    declare cur=${{COMP_WORDS[COMP_CWORD]}}
    if [[ ${{COMP_CWORD}} -eq 1 ]]
    then
        _filedir -d
    elif [[ -f "{tags_file}" ]] && [[ ! ${{COMP_WORDS[1]}} = -* ]]
    then
        COMPREPLY+=($(compgen -W "`cat {tags_file}`" -- $cur))
    fi
}}

_e() {{
    declare cur=${{COMP_WORDS[COMP_CWORD]}}
    if [[ ${{COMP_CWORD}} -eq 1 ]]
    then
        if [[ -f "{tags_file}" ]]
        then
            COMPREPLY+=($(compgen -W "`cat {tags_file}`" -- $cur))
        fi
        COMPREPLY+=($(compgen -W "-p" -- $cur))
    elif [[ ${{COMP_CWORD}} -eq 2 && ${{COMP_WORDS[1]}} = -p ]]
    then
        if [[ -f "{tags_file}" ]]
        then
            COMPREPLY+=($(compgen -W "`cat {tags_file}`" -- $cur))
        fi
    fi
}}

_d() {{
    declare cur=${{COMP_WORDS[COMP_CWORD]}}
    if [[ ${{COMP_CWORD}} -eq 1 ]]
    then
        if [[ -f "{tags_file}" ]]
        then
            COMPREPLY+=($(compgen -W "`cat {tags_file}`" -- $cur))
        fi
    fi
}}

complete -o dirnames -F _dtags dtags
complete -o dirnames -F _t t
complete -o dirnames -F _u u
complete -o dirnames -F _e e
complete -o dirnames -F _e p
complete -o dirnames -F _d d

eval "`dtags-refresh bash`"
"""
