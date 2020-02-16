#!/bin/bash
###
#
# Installation der Skripte in diesem Verzeichnis auf der Zielmaschine.
#

for i in `ls *.bash`
do
  cp $i /usr/local/bin
  chmod 755 /usr/local/bin/$i
done

ls -ali /usr/local/bin/*.bash

