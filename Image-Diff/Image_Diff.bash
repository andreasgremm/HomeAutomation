#!/bin/bash
#
#  Prozedur zur Reduzierung der Bilder aus der Bewegungserkennung 
#  (z.B.: IP Kamera nimmt 30 Sekunden auf, allerdings findet die Bewegung nur 10 Sekunden lang statt)
#
#

if [ "$#" -ne 2 ] 
then
  echo "Usage: $0 Eingangsbilderverzeichnis Ausgangsbilderverzeichnis" >&2
  echo "Example: $0 /home/pictures/camera /home/pictures/differenzreduziert" >&2
  exit 1
fi

imagedir=$1
diffdir=$2

declare -i piccount
declare -i diffpic
declare -i diffvalue

piccount=0
diffpic=0

if [ -f $imagedir/Thumbs.db ]
then
	rm -f $imagedir/Thumbs.db
fi

for i in $( find $imagedir -type f -name '*.jpg' ); do 
	if [ $piccount -eq 0 ]
	then
		pic1=`basename $i`
	fi

	piccount+=1

	if [ $piccount -ge 2 ]
	then
		pic2=`basename $i`
	fi

	if [ $piccount -ge 2 ]
	then
		echo "Verarbeite :" $pic1 $pic2

		diffvalue=`convert -compare -metric AE -fuzz 15% $imagedir/$pic1 $imagedir/$pic2 -format "%[distortion]" info:`

		if [ $diffvalue -gt 100 ]
		then

			if [ ! -f $diffdir/$pic1 ]
			then
				insstring=$( echo $pic1  | cut -f 2 -d"_" | cut -c1-14 )
				convert $imagedir/$pic1 -quality 100 -auto-gamma -gravity SouthEast -fill yellow -annotate 0 "$insstring" $diffdir/$pic1
			fi
			rm -f $imagedir/$pic1

			if [ ! -f $diffdir/$pic2 ]
			then
				insstring=$( echo $pic2  | cut -f 2 -d"_" | cut -c1-14 )
				convert $imagedir/$pic2 -quality 100 -auto-gamma -gravity SouthEast -fill yellow -annotate 0 "$insstring" $diffdir/$pic2
			fi

			diffpic+=1
		else
			rm -f $imagedir/$pic1
		fi

		pic1=$pic2

	fi
done
