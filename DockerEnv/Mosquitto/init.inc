mkdir /var/lib/mosquitto
mkdir /var/log/mosquitto
mkdir /etc/mosquitto
cp logrotate.conf /etc/logrotate.d/mosquitto
cp -r ./conf/* /etc/mosquitto/

docker run -it --entrypoint /bin/chown -p 1883:1883 -p 9001:9001 \
    -v /etc/mosquitto/:/mosquitto/config/:ro \
    -v /var/lib/mosquitto/:/mosquitto/data/ \
    -v /var/log/mosquitto/:/mosquitto/log/ \
    eclipse-mosquitto  mosquitto:mosquitto /mosquitto/data /mosquitto/log

# Bitte ein Mosquitto-Password File in /etc/mosquitto/pwfile ablegen!!!
