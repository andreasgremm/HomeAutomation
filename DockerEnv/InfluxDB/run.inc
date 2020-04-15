docker run -d --name influx \
      --restart unless-stopped \
      -p 8086:8086 \
      -v /usr/local/etc/influxdb/influxdb.conf:/etc/influxdb/influxdb.conf:ro \
      -v /var/lib/influxdb:/var/lib/influxdb \
      -v /etc/localtime:/etc/localtime:ro \
      -v /etc/timezone:/etc/timezone:ro \
      influxdb
