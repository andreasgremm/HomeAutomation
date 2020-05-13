docker run -d --name=grafana \
    -p 3000:3000 \
    --restart unless-stopped \
    -v /usr/local/etc/grafana/:/etc/grafana/ \
    -v /var/lib/grafana/:/var/lib/grafana/ \
    -v /etc/localtime:/etc/localtime:ro \
    -v /etc/timezone:/etc/timezone:ro \
    grafana/grafana:master-ubuntu 
