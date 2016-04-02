CONFIGURATION = """
unalias d &> /dev/null

function d() {{
    declare _dtags_usage='{usage}'
    declare _dtags_version='{version}'
    declare _dtags_description='{description}'
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
        printf "%sToo many arguments\n" "$_dtags_usage"
        return 2
    fi
    declare -a _dtags_dirs

    PREV_IFS=$IFS
    IFS=$'\n'
    _dtags_dirs=($(grep -F ,$1, {mapping_file} | cut -d',' -f1))
    IFS=$PREV_IFS
    declare _dtags_count=${{#_dtags_dirs[@]}}

    if [[ $_dtags_count -eq 0 ]]
    then
        if [[ -d $1 ]]
        then
            declare _dtags_dir="$1"
        else
            printf "$_dtags_dest_err" "$_dtags_usage" "$1"
            return 2
        fi
    elif [[ $_dtags_count = 1 ]]
    then
        declare _dtags_dir=${{_dtags_dirs[1]}}
    else
        for i in `seq $_dtags_count`
        do
            printf "$_dtags_choice" "$i" "${{_dtags_dirs[$i]}}"
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
        declare _dtags_dir=${{_dtags_dirs[$_dtags_idx]}}
    fi
    if [[ -d $_dtags_dir ]]
    then
        cd "$_dtags_dir"
        return 0
    else
        printf "$_dtags_dest_err" "$_dtags_usage" "$_dtags_dir"
        return 2
    fi
}}

__dtags_d_command() {{
    if [[ CURRENT -eq 2 ]]
    then
        if [[ -f "{tags_file}" ]]
        then
            compadd -S '' `cat {tags_file}`
        fi
        _files -/
    fi
}}


__dtags_e_command() {{
    if [[ CURRENT -eq 2 ]]
    then
        [[ -f "{tags_file}" ]] && compadd `cat {tags_file}`
        compadd -- -p
        _files -/
    elif [[ CURRENT -eq 3 && $words[2] = -p ]]
    then
        [[ -f "{tags_file}" ]] && compadd `cat {tags_file}`
        _files -/
    elif [[ CURRENT -gt 3 ]]
    then
        _files
    fi
}}


__dtags_tag_untag_commands() {{
    if [[ CURRENT -eq 2 ]]
    then
        _files -/
    elif [[ -f "{tags_file}" ]] && [[ ! $words[2] = -* ]]
    then
        compadd `cat {tags_file}`
    fi
}}


__dtags_main_command() {{
    if [[ CURRENT -eq 2 ]]
    then
        compadd list reverse shell
        compadd -S '' edit clean
    elif [[ $words[2] = list || $words[2] = reverse ]]
    then
        [[ -f "{tags_file}" ]] && compadd -S '' `cat {tags_file}`
        _files -/
    fi
}}

compdef __dtags_e_command e
compdef __dtags_d_command d
compdef __dtags_main_command dtags
compdef __dtags_tag_untag_commands tag untag
"""
