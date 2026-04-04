#!/bin/bash

W=80
H=30
INPUT="rickroll.mp4"
OUTPUT="rickroll.ascii"

start="${EPOCHREALTIME/./}"

ffmpeg -i ${INPUT} -vf "scale=$(( W * 2 )):$(( H * 2 )),format=rgb24" -f rawvideo - 2>/dev/null \
    | python3 to_ascii.py "$W" "$H" > ${OUTPUT}

end="${EPOCHREALTIME/./}"
elapsed=$(( end - start ))
elapsed_fmt="${elapsed: 0:-6}.${elapsed: -6}"
echo "Done in ${elapsed_fmt}s"
