#!/bin/bash

mount /mnt/synology

if [ ! -d "/mnt/synology/Wohnzimmer_Diffs" ]; then
  echo "Input Directory not found"
  umount /mnt/synology
  exit
fi

# /usr/local/bin/pictures2video.bash /mnt/synology/Wohnzimmer_Diffs /mnt/synology/video Wohnzimmer
docker run \
    -it --rm \
    --user `id -u`:`id -g` \
    -v "/mnt/synology/Wohnzimmer_Diffs":"/mnt/pictures_input" \
    -v "/mnt/synology/video":"/mnt/video_output" \
    pictures2video:prod \
    /mnt/pictures_input /mnt/video_output Wohnzimmer

umount /mnt/synology
