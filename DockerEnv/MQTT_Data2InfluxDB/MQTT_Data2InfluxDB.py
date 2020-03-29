###
# based on: https://github.com/ayush-sharma/infra_helpers

import argparse
import atexit
import datetime
from signal import SIGABRT, SIGINT, SIGTERM, signal
from urllib.parse import urlparse

import paho.mqtt.client as paho
from influxdb import InfluxDBClient

from Security.InfluxDB import (DefaultInfluxDB, DefaultInfluxDBPassword,
                               DefaultInfluxDBUser)
from Security.MQTT import DefaultMQTTPassword, DefaultMQTTUser

influxdb_config = {}
tr = {"auto": "AUTO", "wohnzimmer": "Wohnzimmer"}
debug = True


def write2DB(measurement, tags, timestamp, fields):
    influxdb_client = InfluxDBClient(
        influxdb_config["influxdb_host"],
        influxdb_config["influxdb_port"],
        influxdb_config["influxdb_user"],
        influxdb_config["influxdb_password"],
        influxdb_config["influxdb_database"],
    )
    influxdb_data = []
    data_point = {
        "measurement": measurement,
        "tags": tags,
        "time": timestamp,
        "fields": fields,
    }
    influxdb_data.append(data_point)
    if debug:
        print(
            "Data: ", influxdb_data, flush=True,
        )
    influxdb_client.write_points(influxdb_data)


# Define event callbacks
def on_connect(mosq, obj, flags, rc):
    if debug:
        print(
            "Connect client: " + mosq._client_id.decode() + ", rc: " + str(rc),
            flush=True,
        )
    mqttc.publish(
        "clientstatus/" + mosq._client_id.decode(), "ONLINE", 0, True
    )
    mqttc.subscribe([("temperatur/+", 2), ("licht/+", 2)])


def on_disconnect(mosq, obj, rc):
    print(
        "Disconnect client: " + mosq._client_id.decode() + ", rc: " + str(rc)
    )


def on_message(mosq, obj, msg):
    if debug:
        print(
            "Message received: "
            + msg.topic
            + ", QoS = "
            + str(msg.qos)
            + ", Payload = "
            + msg.payload.decode(),
            flush=True,
        )


def manage_light(mosq, obj, msg):
    if debug:
        print(
            "Message received (manage_light): "
            + msg.topic
            + ", QoS = "
            + str(msg.qos)
            + ", Payload = "
            + msg.payload.decode(),
            flush=True,
        )

    fields = {"light": int(msg.payload.decode())}
    tags = {"room": tr[msg.topic.split("/")[1]]}
    write2DB(
        "Helligkeit", tags, datetime.datetime.utcnow().isoformat(), fields
    )


def manage_temperatur(mosq, obj, msg):
    if debug:
        print(
            "Message received (manage_temperatur): "
            + msg.topic
            + ", QoS = "
            + str(msg.qos)
            + ", Payload = "
            + msg.payload.decode(),
            flush=True,
        )

        fields = {"temperatur": float(msg.payload.decode())}
        tags = {"room": tr[msg.topic.split("/")[1]]}
        write2DB(
            "Temperatur", tags, datetime.datetime.utcnow().isoformat(), fields
        )


def on_publish(mosq, obj, mid):
    print("mid: " + str(mid))


def on_subscribe(mosq, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_unsubscribe(mosq, obj, mid):
    print("UNSubscribed: " + str(mid))


def on_log(mosq, obj, level, string):
    print(string)


@atexit.register
def cleanup_final():
    print("Cleaning up: " + client_id)


def cleanup(sig, frame):
    print("Signal: ", str(sig), " - Cleaning up", client_id)
    mqttc.publish("clientstatus/" + client_id, "OFFLINE", 0, True)
    mqttc.disconnect()


if __name__ == "__main__":
    """ Define the Parser for the command line"""
    parser = argparse.ArgumentParser(description="MQTT Data2InfluxDB.")
    parser.add_argument(
        "-b",
        "--broker",
        help="IP Adress des MQTT Brokers",
        dest="mqttBroker",
        default="localhost",
    )
    parser.add_argument(
        "-p",
        "--port",
        help="Port des MQTT Brokers",
        dest="port",
        default="1883",
    )
    parser.add_argument(
        "-c",
        "--client-id",
        help="Id des Clients",
        dest="clientID",
        default="MQTT_Data2InfluxDB",
    )
    parser.add_argument(
        "-u",
        "--user",
        help="Broker-Benutzer",
        dest="user",
        default=DefaultMQTTUser,
    )
    parser.add_argument(
        "-P",
        "--password",
        help="Broker-Password",
        dest="password",
        default=DefaultMQTTPassword,
    )
    parser.add_argument(
        "-ip",
        "--influxdb-port",
        help="Port der InfluxDB Datenbank",
        dest="influxdb_port",
        default=8086,
    )
    parser.add_argument(
        "-ih",
        "--influxdb-host",
        help="Hostname/IP der InfluxDB Datenbank",
        dest="influxdb_host",
        default="localhost",
    )
    parser.add_argument(
        "-id",
        "--influxdb-database",
        help="Name der InfluxDB Datenbank",
        dest="influxdb_database",
        default=DefaultInfluxDB,
    )
    parser.add_argument(
        "-iu",
        "--influxdb-user",
        help="InfluxDB-Benutzer",
        dest="influxdb_user",
        default=DefaultInfluxDBUser,
    )
    parser.add_argument(
        "-iP",
        "--influxdb-password",
        help="InfluxDB-Password",
        dest="influxdb_password",
        default=DefaultInfluxDBPassword,
    )
    args = parser.parse_args()
    options = vars(args)

    for sig in (SIGABRT, SIGINT, SIGTERM):
        signal(sig, cleanup)

    client_id = options["clientID"]
    influxdb_config = {
        "influxdb_host": options["influxdb_host"],
        "influxdb_port": options["influxdb_port"],
        "influxdb_user": options["influxdb_user"],
        "influxdb_password": options["influxdb_password"],
        "influxdb_database": options["influxdb_database"],
    }
    mqttc = paho.Client(client_id=client_id, clean_session=True)

    # Assign event callbacks
    mqttc.on_message = on_message
    mqttc.message_callback_add("licht/+", manage_light)
    mqttc.message_callback_add("temperatur/+", manage_temperatur)
    mqttc.on_connect = on_connect
    mqttc.on_disconnect = on_disconnect
    #   mqttc.on_publish = on_publish
    #   mqttc.on_subscribe = on_subscribe
    #   mqttc.on_unsubscribe = on_unsubscribe
    #   mqttc.on_log = on_log

    # Parse CLOUDMQTT_URL (or fallback to localhost)
    # mqtt://user:password@server:port
    url_str = (
        "mqtt://"
        + options["user"]
        + ":"
        + options["password"]
        + "@"
        + options["mqttBroker"]
        + ":"
        + options["port"]
    )
    url = urlparse(url_str)

    # Connect
    mqttc.username_pw_set(url.username, url.password)
    mqttc.will_set("clientstatus/" + client_id, "OFFLINE", 0, True)
    mqttc.connect_async(url.hostname, url.port)

    mqttc.loop_forever(retry_first_connection=True)
