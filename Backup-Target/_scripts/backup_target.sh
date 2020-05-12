#!/bin/bash
#
###
#
# Backup Raspberry Pi or other Systems 
#
# based on: http://guficulo.blogspot.de/2015/04/backup-your-raspberry-pi-automatically.html
#
#   Parameter 1: Logischer Server Name
#   Parameter 2: Hostname / IP-Adresse
# Beispiel:
#  /volume1/Backups/_scripts/backup_target.sh PI_Homeautomation 192.168.0.1
#
if [ "$#" -ne 2 ] 
then
  echo "Usage: $0 Logischer-Server-Name HOST-to-Backup" >&2
  echo "Example: backup_target.sh PI_Homeautomation 192.168.0.1" >&2
  exit 1
fi
SERVER=$1
ADDRESS=$2

DIRECTORY=/volume1/Backups

NOW=$(date +"%Y-%m-%d")
LOGFILE="$SERVER-$NOW.log"
/bin/rsync -av --delete --delete-excluded --force --exclude-from=$DIRECTORY/_scripts/rsync-exclude.txt -e "ssh -p 22" root@$ADDRESS:/ $DIRECTORY/$SERVER/ >>$DIRECTORY/logs/$LOGFILE 2>&1
