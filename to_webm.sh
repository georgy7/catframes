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
        echo "    to_webm.sh [--delete-jpegs]"
        echo
        exit 0
    elif [ "$1" != "--delete-jpegs" ]; then
        echo "Unknown parameter \"$1\". Use to_webm.sh --help."
        exit 1
    fi
fi

# Lexicographical (default) order is the best for surveillance data.
for f in *.jpg; do echo "file '$f'" >> list.txt; done
ffmpeg -f concat -r 1 -i list.txt -r 1 output.webm

FFMPEG_ERROR_CODE=$?

if [ $FFMPEG_ERROR_CODE == 0 ]; then
    if [ $# -ne 0 ]; then
        if [ "$1" == "--delete-jpegs" ]; then
            find . -name "*.jpg" -type f -delete
        fi
    fi
else
    echo "ffmpeg error $FFMPEG_ERROR_CODE"
fi
