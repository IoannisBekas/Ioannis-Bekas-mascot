#!/usr/bin/env bash
# Grade a raw Kling clip to the #f5f5f5 background and encode desktop + mobile web versions.
# usage: scripts/encode.sh video/raw/sceneN.mp4 out/sceneN
set -euo pipefail
src="$1"; out="$2"
# Same curve as flatten.py: <175 untouched, 175–226 stretched up, >=226 clamped to 245 (#f5f5f5).
L="if(lt(val\,175)\,val\,if(lt(val\,226)\,175+(val-175)*70/51\,245))"
grade="format=rgb24,lutrgb=r='$L':g='$L':b='$L'"

# Desktop: 1920x1080.
ffmpeg -v error -y -i "$src" -vf "$grade,scale=1920:1080:flags=lanczos,format=yuv420p" \
  -c:v libx264 -preset slow -crf 23 -profile:v high -movflags +faststart -an "$out.mp4"
# Mobile: left 54% of the frame (where the puppet stands), 720 wide.
ffmpeg -v error -y -i "$src" -vf "$grade,crop=iw*0.54:ih:0:0,scale=720:-2:flags=lanczos,format=yuv420p" \
  -c:v libx264 -preset slow -crf 24 -profile:v high -movflags +faststart -an "${out}_m.mp4"
# Posters: first and last frame.
ffmpeg -v error -y -i "$out.mp4" -frames:v 1 -q:v 3 "${out}_first.jpg"
ffmpeg -v error -y -sseof -0.1 -i "$out.mp4" -frames:v 1 -q:v 3 "${out}_last.jpg"
