docker run -d --name influx \
      -p 8086:8086 \
      -v $PWD/etc/influxdb.conf:/etc/influxdb/influxdb.conf:ro \
      -v $PWD/db:/var/lib/influxdb \
      -v /etc/localtime:/etc/localtime:ro \
      -v /etc/timezone:/etc/timezone:ro \
      influxdb
