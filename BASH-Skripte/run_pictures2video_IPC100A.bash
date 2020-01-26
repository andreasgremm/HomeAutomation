#!/bin/bash

mount /mnt/synology
if [ ! -d "/mnt/synology/IPC100A_Diffs" ]; then
  echo "Input Directory not found"
  umount /mnt/synology
  exit
fi

/usr/local/bin/pictures2video.bash /mnt/synology/IPC100A_Diffs /mnt/synology/video IPC100A

umount /mnt/synology
