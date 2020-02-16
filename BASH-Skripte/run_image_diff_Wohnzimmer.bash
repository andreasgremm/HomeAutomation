#!/bin/bash
#
####
#
#     Start Image_Diff for Wohnzimmer_Cam on the Homeautomation Server
#
mount /mnt/synology
mount /mnt/mediencenter

if [ ! -d "/mnt/mediencenter/Hochgeladen" ]; then
  echo "Input Directory not found"
  umount /mnt/synology
  umount /mnt/mediencenter
  exit
fi

if [ ! -d "/mnt/synology/Wohnzimmer_Diffs" ]; then
  echo "Output Directory not found"
  umount /mnt/synology
  umount /mnt/mediencenter
  exit
fi

# /usr/local/bin/Image_diff.bash /mnt/mediencenter/Hochgeladen /mnt/synology/Wohnzimmer_Diffs
docker run \
	-it --rm \
	-v "/mnt/mediencenter/Hochgeladen":"/mnt/camera_input" \
	-v "/mnt/synology/Wohnzimmer_Diffs":"/mnt/reduced_output" \
	imagediff:prod 

umount /mnt/synology
umount /mnt/mediencenter
