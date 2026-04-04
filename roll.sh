#!/bin/bash

VIDEO_URL="https://github.com/tenk28/rickroll/raw/refs/heads/master/rickroll.ascii"
AUDIO_URL="https://github.com/tenk28/rickroll/raw/refs/heads/master/rickroll.wav"
FPS="30"

# Frame duration in microseconds (integer)
FRAME_US=$(( 1000000 / FPS ))

cleanup() {
    printf '\033[?25h\n'
    kill $AUDIO_PID 2>/dev/null
    exit
}

trap cleanup INT TERM

curl -sL "$AUDIO_URL" | aplay -q - &
AUDIO_PID=$!

printf '\033[?25l'   # hide cursor
printf '\033[2J'     # clear screen

frame=""
frame_start="${EPOCHREALTIME/./}"   # microseconds as integer, no subprocess
while IFS= read -r line; do
    if [[ "$line" == "---FRAME---" ]]; then
        printf '\033[H'
        printf '%s' "$frame"
        frame=""

        now="${EPOCHREALTIME/./}"
        elapsed=$(( now - frame_start ))
        remaining=$(( FRAME_US - elapsed ))
        if (( remaining > 0 )); then
            sleep "${remaining}e-6"   # sleep accepts scientific notation
        fi

        frame_start="${EPOCHREALTIME/./}"
    else
        frame+="$line"$'\n'
    fi
done < <(curl -sL "$VIDEO_URL")

cleanup
