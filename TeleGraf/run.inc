docker run -d --name telegraf \
   -v /opt/vc/bin/vcgencmd:/opt/vc/bin/vcgencmd \
   -v /usr/local/etc/telegraf.conf:/etc/telegraf/telegraf.conf:ro telegraf
