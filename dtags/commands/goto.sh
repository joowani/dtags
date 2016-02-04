#!/usr/bin/env bash

goto() {
    usage='usage: goto <tag>'
    description="dtags - go to the directory with the given tag

    If there are multiple directory paths associated with
    the given tag, a selection menu is displayed to allow
    the user to choose which specific directory to go to.

    positional arguments:
      <tag>        the directory tag name

    optional arguments:
      -h, --help  show this help message and exit"

    if [[ $# -gt 1 ]]; then
        printf '%s\ngoto: error: too many arguments\n' "${usage}"
        exit 2  # EINVAL
    elif [[ $# -lt 1 ]]; then
        printf '%s\ngoto: error: argument required: <tag>\n' "${usage}"
        exit 2  # EINVAL
    elif [[ ${1} = '-h' ]] || [[ ${1} == '--help' ]]; then
        printf '%s\n\n%s' "${usage}" "${description}"
        exit 0
    fi
    dirpaths=($(paths ${1}))
    echo $dirpaths
    echo ${dirpaths[1]}
    if [[ ${#dirpaths[@]} -eq 1 ]]; then
        cd ${dirpaths[1]}
    fi
}