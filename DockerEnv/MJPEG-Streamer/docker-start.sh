#!/bin/sh
set -e

export LD_LIBRARY_PATH="/home/mjpegstreamer"
cd /home/mjpegstreamer
/home/mjpegstreamer/mjpg_streamer -i "$3" -o "$1" --output "$2" 
