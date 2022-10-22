#!/bin/bash

mount /mnt/synologyDS920
if [ ! -d "/mnt/synologyDS920/IPC100A_Diffs" ]; then
  echo "Input Directory not found"
  umount /mnt/synologyDS920
  exit
fi

# /usr/local/bin/pictures2video.bash /mnt/synologyDS920/IPC100A_Diffs /mnt/synologyDS920/video IPC100A
docker run \
    -a stdout -a stderr --rm \
    --user `id -u`:`id -g` \
    -v "/mnt/synologyDS920/IPC100A_Diffs":"/mnt/pictures_input" \
    -v "/mnt/synologyDS920/video":"/mnt/video_output" \
    pictures2video:prod \
    /mnt/pictures_input /mnt/video_output IPC100A

umount /mnt/synologyDS920
