#!/bin/bash
###
#
#    Bilder aus einem Verzeichnis in ein Video konvertieren.
#

if [ "$#" -ne 3 ]
then
  echo "Usage: $0 Eingangsbilderverzeichnis Ausgangsvideoverzeichnis Videoname" >&2
  echo "Example: $0 /home/pictures/camera /home/videos Demo" >&2
  exit 1
fi

imagedir="$1"
videodir="$2"
videoname="$3"_$(date +%F_%H-%M).mp4

pushd $imagedir

ls | grep jpg >alle_bilder.txt
ffmpeg  -framerate 1 -pattern_type glob  -i '*.jpg' -c:v libx264 -r 2 -pix_fmt yuv420p "$videodir"/"$videoname"

for i in $(cat alle_bilder.txt)
do
   rm "$i"
done
rm alle_bilder.txt

popd

