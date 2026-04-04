# Generate ASCII video from video

```bash
ffmpeg -i rickroll.mp4 -vf "scale=160:60,format=rgb24" -f rawvideo - 2>/dev/null \
    | python3 to_ascii.py 80 30 > rickroll.ascii
```
