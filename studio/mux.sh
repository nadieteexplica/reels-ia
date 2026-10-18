#!/usr/bin/env bash
# Usage: ./mux.sh <video_dir> <out.mp4>
# Joins frames/f%05d.jpg + audio.wav into a 1080x1920 H.264 reel, loudness -14 LUFS.
set -euo pipefail
dir="$1"; out="$2"
ffmpeg -hide_banner -loglevel error -y \
  -framerate 30 -i "$dir/frames/f%05d.jpg" -i "$dir/audio.wav" \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -profile:v high -r 30 \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11" -c:a aac -b:a 192k -ar 48000 \
  -movflags +faststart -shortest "$out"
ffprobe -v error -show_entries format=duration,size -of default=nw=1 "$out"
