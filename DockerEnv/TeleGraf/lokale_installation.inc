cat /etc/debian_version
wget -qO- https://repos.influxdata.com/influxdb.key | sudo apt-key add -
source /etc/os-release

# Debian 9 Stretch
test $VERSION_ID = "9" && echo "deb https://repos.influxdata.com/debian stretch stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
# Debian 10 Buster
test $VERSION_ID = "10" && echo "deb https://repos.influxdata.com/debian buster stable" | sudo tee /etc/apt/sources.list.d/influxdb.list

apt-get update
apt-get install telegraf
systemctl stop telegraf
usermod -G video telegraf
cp /etc/telegraf/telegraf.conf /etc/telegraf/telegraf.conf.org
cp ./telegraf.conf /etc/telegraf/telegraf.conf
telegraf -config /etc/telegraf/telegraf.conf -test
