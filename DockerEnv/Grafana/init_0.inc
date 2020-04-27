###
#
#  In einer weiteren Session aus dem Container das Verzeichnis /etc/grafana in das lokale Dateisystem kopieren
#
#  docker cp grafana:/etc/grafana /usr/local/etc
#
mkdir -p /usr/local/etc/grafana
mkdir -p /var/lib/grafana

docker run -it --rm --user root --name=grafana -p 3000:3000 \
    --entrypoint bash \
    -v /var/lib/grafana/:/var/lib/grafana/ grafana/grafana:master-ubuntu 
