CONFIGURATION = """
functions -e dtags > /dev/null 2>&1
functions -e t > /dev/null 2>&1
functions -e u > /dev/null 2>&1
functions -e e > /dev/null 2>&1
functions -e p > /dev/null 2>&1
functions -e d > /dev/null 2>&1

function dtags
    dtags-manage $argv; and dtags-refresh fish | source
end

function t
    dtags-t $argv; and dtags-refresh fish | source
end

function u
    dtags-u $argv; and dtags-refresh fish | source
end

function d
    set _dtags_usage "{usage}"
    set _dtags_version "{version}"
    set _dtags_description "{description}"
    if isatty 1
        set _dtags_arg_err "{arg_err_tty}"
        set _dtags_dest_err "{dest_err_tty}"
        set _dtags_input_err "{input_err_tty}"
        set _dtags_idx_err "{index_err_tty}"
        set _dtags_choice "{choice_tty}"
        set -g _dtags_prompt "{prompt_tty}"
    else
        set _dtags_arg_err "{arg_err}"
        set _dtags_dest_err "{dest_err}"
        set _dtags_input_err "{input_err}"
        set _dtags_idx_err "{index_err}"
        set _dtags_choice "{choice}"
        set -g _dtags_prompt "{prompt}"
    end
    if math "1 >" (count $argv) > /dev/null
        cd $HOME
        return 0
    else if [ $argv[1] = "--help" ]
        printf "$_dtags_usage$_dtags_description"
        return 0
    else if [ $argv[1] = "--version" ]
        printf "Version %s\n" "$_dtags_version"
        return 0
    else if [ $argv[1] = "-" ]
        cd "$OLDPWD"
        return 0
    else if echo "$argv[1]" | grep -q -E '^-' > /dev/null
        printf "$_dtags_arg_err" "$_dtags_usage" "$argv[1]"
        return 2
    else if math "1 <" (count $argv) > /dev/null
        printf "%sd: too many arguments\n" "$_dtags_usage"
        return 2
    end
    set _dtags_dirs (grep -F ,$argv[1], {mapping_file} | cut -d',' -f1)
    set -g _dtags_count (count $_dtags_dirs)
    if math "$_dtags_count == 0" > /dev/null
        if test -d $argv[1]
            set _dtags_dir $argv[1]
        else
            printf "$_dtags_dest_err" "$argv[1]"
            return 2
        end
    else if math "$_dtags_count == 1" > /dev/null
        set _dtags_dir $_dtags_dirs[1]
    else
        for i in (seq $_dtags_count)
            printf "$_dtags_choice" "$i" "$_dtags_dirs[$i]"
        end
        function _dtags_prompt_func
            printf "$_dtags_prompt" "$_dtags_count"
        end
        read -l -p _dtags_prompt_func _dtags_idx
        functions --erase _dtags_prompt_func
        if not echo "$_dtags_idx" | grep -q -E '^[0-9]+$' > /dev/null
            printf "$_dtags_input_err" "$_dtags_idx"
            return 2
        else if math "$_dtags_idx > $_dtags_count" > /dev/null
            printf "$_dtags_idx_err" "$_dtags_idx"
            return 2
        end
        set _dtags_dir $_dtags_dirs[$_dtags_idx]
    end
    if test -d $_dtags_dir
        cd $_dtags_dir
        return 0
    else
        printf "$_dtags_dest_err" "$_dtags_dir"
        return 2
    end
end

function __dtags_no_args
  set cmd (commandline -opc)
  if [ (count $cmd) -eq 1 ]
    return 0
  end
  return 1
end

function __dtags_one_arg
  set cmd (commandline -opc)
  if [ (count $cmd) -eq 2 ]
    return 0
  end
  return 1
end


function __dtags_has_first_arg
  set cmd (commandline -opc)
  if [ (count $cmd) -gt 1 ]
    if [ $argv[1] = $cmd[2] ]
      return 0
    end
  end
  return 1
end

function __dtags_past_first_arg
  set cmd (commandline -opc)
  if [ (count $cmd) -gt 1 ]
    return 0
  end
  return 1
end

function __dtags_tags
    if test -f {tags_file}
        cat {tags_file}
    end
end

complete -f -c dtags -n '__dtags_no_args' \
    -a list -d 'Display directories-to-tags mapping'
complete -f -c dtags -n '__dtags_no_args' \
    -a reverse -d 'Display tags-to-directories mapping'
complete -f -c dtags -n '__dtags_no_args' \
    -a edit -d 'Edit tags and directories via editor'
complete -f -c dtags -n '__dtags_no_args' \
    -a clean -d 'Remove invalid tags and directories'
complete -f -c dtags -n '__dtags_no_args' \
    -a shell -d 'Print the shell runtime configuration'
complete -f -c dtags -n '__dtags_no_args' \
    -a commands -d 'List all available dtags commands'
complete -f -c dtags -n '__dtags_has_first_arg list' \
    -a '(__dtags_tags)' -d 'Directory tag'
complete -f -c dtags -n '__dtags_has_first_arg reverse' \
    -a '(__dtags_tags)' -d 'Directory tag'

complete -f -c t -n '__dtags_past_first_arg' \
    -a '(__dtags_tags)' -d 'Directory tag'

complete -f -c u -n '__dtags_past_first_arg' \
    -a '(__dtags_tags)' -d 'Directory tag'

complete -f -c e -n '__dtags_no_args' \
    -a '(__dtags_tags)' -d 'Directory tag'

complete -f -c p -n '__dtags_no_args' \
    -a '(__dtags_tags)' -d 'Directory tag'

complete -f -c d -n '__dtags_no_args' \
-a '(__dtags_tags)' -d 'Directory tag'

dtags-refresh fish | source
"""
