docker run -it --rm --user root --name=grafana -p 3000:3000 \
    --entrypoint bash \
    -v /usr/local/etc/grafana/:/etc/grafana/ \
    -v /var/lib/grafana/:/var/lib/grafana/ grafana/grafana:master-ubuntu 
