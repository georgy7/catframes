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
        echo "    images_to_h264.sh [--delete-images]"
        echo
        exit 0
    elif [ "$1" != "--delete-images" ]; then
        echo "Unknown parameter \"$1\". Use images_to_h264.sh --help."
        exit 1
    fi
fi

shopt -s nullglob

rm list.txt
# Lexicographical (default) order is the best for surveillance data.
for f in *.{jpg,jpeg,png,JPG,JPEG,PNG}; do echo "file '$f'" >> list.txt; echo "duration 1" >> list.txt; done
ffmpeg -f concat -safe 0 -i list.txt -c:v libx264 -preset slow -tune fastdecode -crf 35 -r 1 output.mkv

FFMPEG_ERROR_CODE=$?

if [ $FFMPEG_ERROR_CODE == 0 ]; then
    if [ $# -ne 0 ]; then
        if [ "$1" == "--delete-images" ]; then
            for f in *.{jpg,jpeg,png,JPG,JPEG,PNG}; do rm "$f"; done
        fi
    fi
else
    echo "ffmpeg error $FFMPEG_ERROR_CODE"
fi
