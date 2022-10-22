#!/bin/bash
#
####
#
#     Start Image_Diff for IPC100A on the Homeautomation Server
#
mount /mnt/synologyDS920

if [ ! -d "/mnt/synologyDS920/FTP" ]; then
  echo "Input Directory not found"
  umount /mnt/synologyDS920
  exit
fi

if [ ! -d "/mnt/synologyDS920/IPC100A_Diffs" ]; then
  echo "Output Directory not found"
  umount /mnt/synologyDS920
  exit
fi

# /usr/local/bin/Image_diff.bash /mnt/synologyDS920/FTP /mnt/synologyDS920/IPC100A_Diffs
docker run \
    -a stdout -a stderr  --rm \
    --user `id -u`:`id -g` \
    -v "/mnt/synologyDS920/FTP":"/mnt/camera_input" \
    -v "/mnt/synologyDS920/IPC100A_Diffs":"/mnt/reduced_output" \
    imagediff:prod 

umount /mnt/synologyDS920
