#!/usr/bin/env bash

if [ $# -ne 0 ]; then
    if [ "$1" == "help" ] || \
       [ "$1" == "h" ] || \
       [ "$1" == "-help" ] || \
       [ "$1" == "--help" ] || \
       [ "$1" == "-h" ] || \
       [ "$1" == "usage" ] || \
       [ "$1" == "u" ] || \
       [ "$1" == "-usage" ] || \
       [ "$1" == "--usage" ] || \
       [ "$1" == "-u" ]; then
        echo
        echo "    jpegs_to_h264.sh [--delete-jpegs]"
        echo
        exit 0
    elif [ "$1" != "--delete-jpegs" ]; then
        echo "Unknown parameter \"$1\". Use jpegs_to_h264.sh --help."
        exit 1
    fi
fi

rm list.txt
# Lexicographical (default) order is the best for surveillance data.
for f in *.jpg; do echo "file '$f'" >> list.txt; echo "duration 1" >> list.txt; done
ffmpeg -f concat -safe 0 -i list.txt -c:v libx264 -preset fast -tune fastdecode -crf 40 -r 1 output.mkv

FFMPEG_ERROR_CODE=$?

if [ $FFMPEG_ERROR_CODE == 0 ]; then
    if [ $# -ne 0 ]; then
        if [ "$1" == "--delete-jpegs" ]; then
            for f in *.jpg; do rm "$f"; done
        fi
    fi
else
    echo "ffmpeg error $FFMPEG_ERROR_CODE"
fi
