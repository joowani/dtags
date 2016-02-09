import os
import sys

from dtags import SHELL, TAGS_FILE, MAPPING_FILE


runtime_configuration = """

#!/usr/bin/env {shell}

goto() {{

usage="usage: goto destination"
help="dtags - go to the tagged directory

If there are multiple directory paths associated with
a given tag, a selection menu is displayed to let the
user choose which specific directory to go to.

positional arguments:
  destination      the directory tag name or path

optional arguments:
  -h, --help       show this help message and exit"

if [[ $# -gt 1 ]]; then
    printf "%s\ndtags: goto: error: too many arguments\n" "${{usage}}"
    return 2
elif [[ $# -lt 1 ]]; then
    printf "%s\ndtags: goto: error: too few arguments\n" "${{usage}}"
    return 2
elif [[ ${{1}} == "-h" ]] || [[ ${{1}} == "--help" ]]; then
    printf "%s\n\n%s\n" "${{usage}}" "${{help}}"
    return 0
elif [[ ${{1}} == -* ]]; then
    printf "%s\ndtags: goto: error: unrecognized argument: %s\n" \
           "${{usage}}" "${{1}}"
    return 2
fi
if [[ -d ${{1}} ]]; then
    cd ${{1}}
else
    dirpaths=(`grep -E "(^| )${{1}}( |$)" "{mapping_file}" | cut -d' ' -f1`)
    if [[ ${{#dirpaths[@]}} == 0 ]]; then
        return 1
    elif (( ${{#dirpaths[@]}} == 1 )); then
        dirpath="${{${{dirpaths[1]}}/#\~/${{HOME}}}}"
        if [[ -d ${{dirpath}} ]]; then
            cd ${{dirpath}}
        else
            printf "dtags: goto: error: invalid directory: %s\n" "${{dirpath}}"
            return 2
        fi
    else
        count=1
        for dirpath in "${{dirpaths[@]}}"; do
            printf "%s: %s\n" "${{count}}" "${{dirpath}}"
            ((++count))
        done
        printf "\nSelect directory (1 - %s): " "${{#dirpaths[@]}}"
        read num
        if [[ ! ${{num}} =~ ^-?[0-9]+$ ]]; then
            printf "dtags: goto: error: invalid input: %s\n" "${{num}}"
            return 2
        elif [[ ${{num}} -gt ${{#dirpaths[@]}} ]] || [[ ${{num}} -lt 1 ]]; then
            printf "dtags: goto: error: index out of range: %s\n" "${{num}}"
            return 2
        fi
        cd "${{${{dirpaths[${{num}}]}}/#\~/${{HOME}}}}"
    fi
fi
}}

_goto() {{
    if [[ ${{COMP_CWORD}} == 1 ]]; then
        tags="{tags_file}"
        if [[ -f ${{tags}} ]]; then
            COMPREPLY=($(compgen -W "`cat ${{tags}}`"))
        fi
    fi
}}

_run() {{
    tags="{tags_file}"
    if [[ -f ${{tags}} ]]; then
        COMPREPLY=($(compgen -W "`cat ${{tags}}`"))
    fi
}}

complete -F _goto goto
complete -F _run run


""".format(
    mapping_file=MAPPING_FILE,
    tags_file=TAGS_FILE,
    shell=os.path.basename(SHELL)
)


def main():
    sys.stdout.write(runtime_configuration)
    sys.exit(0)
