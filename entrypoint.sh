#!/bin/bash
# Docker entrypoint - runs the captioner on all videos in /videos
set -e

for video in /videos/*.mp4; do
    if [ -f "$video" ]; then
        echo "Processing: $video"
        python captioner.py "$video"
    fi
done

echo "All videos processed!"
