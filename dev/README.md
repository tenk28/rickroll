# Generate ASCII video from video

```bash
ffmpeg -i rickroll.mp4 -vf "scale=80:30,format=rgb24" -f rawvideo - 2>/dev/null \
    | python3 to_ascii.py 40 15 > rickroll.ascii
```
