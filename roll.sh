#!/bin/bash

VIDEO_URL="https://github.com/tenk28/rickroll/raw/refs/heads/master/rickroll.ascii"
AUDIO_URL="https://github.com/tenk28/rickroll/raw/refs/heads/master/rickroll.wav"
FPS="30"
DELAY=$(awk "BEGIN { printf \"%.4f\", 1 / $FPS }")

trap 'printf "\033[?25h\n"; kill $AUDIO_PID 2>/dev/null; exit' INT TERM

# Start audio in background
curl -sL "$AUDIO_URL" | aplay -q - &
AUDIO_PID=$!

printf '\033[?25l'   # hide cursor
printf '\033[2J'     # clear screen

frame=""
while IFS= read -r line; do
    if [[ "$line" == "---FRAME---" ]]; then
        printf '\033[H'
        printf '%s' "$frame"
        frame=""
        sleep "$DELAY"
    else
        frame+="$line"$'\n'
    fi
done < <(curl -sL "$VIDEO_URL")

printf '\033[?25h'   # restore cursor
printf '\n'
kill $AUDIO_PID 2>/dev/null
