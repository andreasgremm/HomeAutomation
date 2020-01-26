#!/bin/bash
if [ ! -d "/mnt/mediencenter/Hochgeladen" ]; then
   su pi -c "mount /mnt/mediencenter"
fi

