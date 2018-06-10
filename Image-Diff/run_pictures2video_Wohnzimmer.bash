#!/bin/bash

mount /mnt/synology

if [ ! -d "/mnt/synology/Wohnzimmer_Diffs" ]; then
  echo "Input Directory not found"
  umount /mnt/synology
  exit
fi

/usr/local/bin/pictures2video.bash /mnt/synology/Wohnzimmer_Diffs /mnt/synology/video Wohnzimmer

umount /mnt/synology
