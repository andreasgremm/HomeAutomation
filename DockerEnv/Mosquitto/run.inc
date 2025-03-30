docker run -d --name mosquitto -p 1883:1883 -p 9001:9001 \
    --restart unless-stopped \
    -v /etc/mosquitto/:/mosquitto/config/:ro \
    -v /var/lib/mosquitto/:/mosquitto/data/ \
    -v /var/log/mosquitto/:/mosquitto/log/ \
    eclipse-mosquitto:2.0.20
