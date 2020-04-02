docker run -d --name=grafana -p 3000:3000 \
    --restart unless-stopped \
    -v /usr/local/etc/grafana/:/etc/grafana/ \
    -v /var/lib/grafana/:/var/lib/grafana/ grafana/grafana:master-ubuntu 
