#!/usr/bin/env bash

OUTPUT=output.mkv
DELETE_IMAGES=false

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
        echo "    images_to_h264.sh [--delete-images] [-o pathToFile.mkv]"
        echo
        echo "      Default output file is \"output.mkv\" in the current folder."
        echo
        echo "    For instance:"
        echo "    \$ cd today_directory"
        echo "    \$ images_fix_resolution.py"
        echo "    \$ images_to_h264.sh --delete-images -o \"/backups/today.mkv\""
        echo
        exit 0
    elif [ "$1" != "--delete-images" ]; then
        if [ "$1" == "-o" ]; then
            if [ $# -gt 1 ]; then
                OUTPUT=$2
                if [ $# -gt 2 ]; then
                    if [ "$3" != "--delete-images" ]; then
                        echo "Unknown parameter \"$3\". Please, use \"--help\"."
                        exit 1
                    else
                        DELETE_IMAGES=true
                    fi
                fi
            else
                echo "There is must be a path after the \"-o\" parameter. Please, use \"--help\"."
                exit 1
            fi
        else
            echo "Unknown parameter \"$1\". Please, use \"--help\"."
            exit 1
        fi
    else
        DELETE_IMAGES=true
        if [ $# -gt 1 ]; then
            if [ "$2" == "-o" ]; then
                if [ $# -gt 2 ]; then
                    OUTPUT=$3
                else
                    echo "There is must be a path after the \"-o\" parameter. Please, use \"--help\"."
                    exit 1
                fi
            else
                echo "Unknown parameter \"$2\". Please, use \"--help\"."
                exit 1
            fi
        fi
    fi
fi

shopt -s nullglob

rm list.txt
# Lexicographical (default) order is the best for surveillance data.
for f in *.{jpg,jpeg,png,JPG,JPEG,PNG}; do echo "file '$f'" >> list.txt; echo "duration 1" >> list.txt; done
ffmpeg -f concat -safe 0 -i list.txt -c:v libx264 -preset slow -tune fastdecode -crf 35 -r 1 $OUTPUT

FFMPEG_ERROR_CODE=$?

if [ $FFMPEG_ERROR_CODE == 0 ]; then
    if [ "$DELETE_IMAGES" = true ]; then
        for f in *.{jpg,jpeg,png,JPG,JPEG,PNG}; do rm "$f"; done
    fi
else
    echo "ffmpeg error $FFMPEG_ERROR_CODE"
fi
