#!/bin/bash
#
####
#
#     Start Image_Diff for Wohnzimmer_Cam on the Homeautomation Server
#
mount /mnt/synologyDS920
mount /mnt/mediencenter

if [ ! -d "/mnt/mediencenter/Hochgeladen" ]; then
  echo "Input Directory not found"
  umount /mnt/synologyDS920
  umount /mnt/mediencenter
  exit
fi

if [ ! -d "/mnt/synologyDS920/Wohnzimmer_Diffs" ]; then
  echo "Output Directory not found"
  umount /mnt/synologyDS920
  umount /mnt/mediencenter
  exit
fi

# /usr/local/bin/Image_diff.bash /mnt/mediencenter/Hochgeladen /mnt/synologyDS920/Wohnzimmer_Diffs
docker run \
    -a stdout -a stderr --rm \
    --user `id -u`:`id -g` \
    -v "/mnt/mediencenter/Hochgeladen":"/mnt/camera_input" \
    -v "/mnt/synologyDS920/Wohnzimmer_Diffs":"/mnt/reduced_output" \
    imagediff:prod 

umount /mnt/synologyDS920
umount /mnt/mediencenter
