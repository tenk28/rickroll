#!/bin/bash

URL="https://github.com/tenk28/rickroll/raw/refs/heads/master/rickroll.ascii"
FPS="30"
DELAY=$(awk "BEGIN { printf \"%.4f\", 1 / $FPS }")

trap 'printf "\033[?25h\n"; exit' INT TERM

printf '\033[?25l'   # hide cursor
printf '\033[2J'     # clear screen

frame=""
while IFS= read -r line; do
    if [[ "$line" == "---FRAME---" ]]; then
        printf '\033[H'       # jump to top-left
        printf '%s' "$frame"  # print entire frame at once
        frame=""
        sleep "$DELAY"
    else
        frame+="$line"$'\n'
    fi
done < <(curl -sL "$URL")

printf '\033[?25h'   # restore cursor
printf '\n'
