#!/bin/bash

mount /mnt/synologyDS920

if [ ! -d "/mnt/synologyDS920/Wohnzimmer_Diffs" ]; then
  echo "Input Directory not found"
  umount /mnt/synologyDS920
  exit
fi

# /usr/local/bin/pictures2video.bash /mnt/synologyDS920/Wohnzimmer_Diffs /mnt/synologyDS920/video Wohnzimmer
docker run \
    -a stdout -a stderr --rm \
    --user `id -u`:`id -g` \
    -v "/mnt/synologyDS920/Wohnzimmer_Diffs":"/mnt/pictures_input" \
    -v "/mnt/synologyDS920/video":"/mnt/video_output" \
    pictures2video:prod \
    /mnt/pictures_input /mnt/video_output Wohnzimmer

umount /mnt/synologyDS920
