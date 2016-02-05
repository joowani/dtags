#!/usr/bin/env bash

goto() {
usage="usage: goto <tag>"
description="dtags - go to the directory with the given tag

If there are multiple directory paths associated with
the given tag, a selection menu is displayed to allow
the user to choose which specific directory to go to.

positional arguments:
  <tag>        the directory tag name

optional arguments:
  -h, --help  show this help message and exit"

if [[ $# -gt 1 ]]; then
    printf "%s\ngoto: error: too many arguments\n" "${usage}"
    return 2
elif [[ $# -lt 1 ]]; then
    printf "%s\ngoto: error: expecting a tag name\n" "${usage}"
    return 2
elif [[ ${1} == '-h' ]] || [[ ${1} == '--help' ]]; then
    printf "%s\n\n%s\n" "${usage}" "${description}"
    return 0
fi
# Run the dtags command 'paths' and store the output
output="$(paths ${1} 2>&1)"
return_code=$?
if [[ ${return_code} != 0 ]]; then
    printf "${output}\n"
    return ${return_code}
fi
directories=($(echo ${output} | tr -d '\n'))
# If there is a 1-1 tag to path mapping, change the directory
if (( ${#directories[@]} == 1 )); then
    cd ${directories[1]}
# Otherwise, list the directories and prompt the user for selection
else
    count=1
    for directory in "${directories[@]}"; do
        printf "%s: %s\n" "${count}" "${directory}"
        ((++count))
    done
    printf "\nSelect directory (1 - %s): " "${#directories[@]}"
    read index
    if [[ ! ${index} =~ ^-?[0-9]+$ ]]; then
        printf "goto: error: invalid input\n"
        return 2
    elif [[ ${index} -gt ${#directories[@]} ]] || [[ ${index} -lt 1 ]]; then
        printf "goto: error: index out of range\n"
        return 2
    fi
    cd ${directories[${index}]}
fi
}
#
#_dtags()
#{
#    local tags
#
#    if [[ -f ~ ]]
#
#
#    COMPREPLY=()
#    tags="@unata @api @bokchoy"
#
#    COMPREPLY=($(compgen -W "${tags}"))
#    return 0
#}
#
#complete -F _dtags goto
#complete -F _dtags run
#complete -F _dtags tags
