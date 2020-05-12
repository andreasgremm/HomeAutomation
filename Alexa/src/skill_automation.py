import logging

import paho.mqtt.publish as publish
from flask import Flask, render_template
from flask_ask import (Ask, context, convert_errors, question, request,
                       session, statement, version)
from Security.MQTT import DefaultMQTTUser, DefaultMQTTPassword

app = Flask(__name__)
ask = Ask(app, "/wsgi/alexa/")
log = logging.getLogger()
logging.basicConfig(level=logging.INFO)

mqttc = {
    "hostname": "192.168.1.237",
    "port": 1883,
    "auth": {"username": DefaultMQTTUser, "password": DefaultMQTTPassword},
}
szenen = {"wohnen eins": "Wohnen1", "wohnen zwei": "Wohnen2", "jump": "Jump"}


@ask.on_session_started
def new_session():
    log.info("+++new session started")


@ask.session_ended
def session_ended():
    log.info("---session ended")
    return "{}", 200


@ask.launch
def launched():
    return question("Herr, was soll ich machen?")


@ask.intent("HueSzeneIntent")
def scene(szene):
    log.info("Request ID: {}".format(request.requestId))
    log.info("Request Type: {}".format(request.type))
    log.info("Request Intent: {}".format(request.intent))
    log.info("Request Timestamp: {}".format(request.timestamp))
    #   log.info("Session New?: {}".format(session.new))
    #   log.info("User ID: {}".format(session.user.userId))
    #   log.info("Alexa Version: {}".format(version))
    #   log.info("Device ID: {}".format(context.System.device.deviceId))

    if szene in szenen.keys():
        try:
            publish.single(
                "hue/scene/on",
                szenen[szene],
                qos=2,
                retain=False,
                hostname=mqttc["hostname"],
                port=mqttc["port"],
                auth=mqttc["auth"],
            )
            speech_text = "Szene %s gesetzt" % szene
        except Exception as err:
            log.error("Error: {}".format(err))
            speech_text = "Fehler beim setzen der Szene %s" % szene
    else:
        speech_text = "Szene %s ist nicht bekannt!" % szene

    return (
        question(speech_text)
        .simple_card("Automation", speech_text)
        .reprompt("Chef, kann ich sonst noch etwas tun?")
    )


@ask.intent("HueOffIntent")
def ausschalten(lichtaus):
    log.info("Request ID: {}".format(request.requestId))
    log.info("Request Type: {}".format(request.type))
    log.info("Request Intent: {}".format(request.intent))
    log.info("Request Timestamp: {}".format(request.timestamp))
    #   log.info("Session New?: {}".format(session.new))
    #   log.info("User ID: {}".format(session.user.userId))
    #   log.info("Alexa Version: {}".format(version))
    #   log.info("Device ID: {}".format(context.System.device.deviceId))

    if lichtaus in ["aus", "ausschalten"]:
        try:
            publish.single(
                "hue/control",
                '{"all":"off"}',
                qos=2,
                retain=False,
                hostname=mqttc["hostname"],
                port=mqttc["port"],
                auth=mqttc["auth"],
            )
            speech_text = "Lichter %s" % lichtaus
        except Exception as err:
            log.error("Error: {}".format(err))
            speech_text = (
                "Fehler beim ausschalten der Lichter mit dem Befehl %s"
                % lichtaus
            )
    else:
        speech_text = "Schluesselwort %s ist nicht bekannt!" % lichtaus

    return (
        question(speech_text)
        .simple_card("Automation", speech_text)
        .reprompt("Edler, kann ich sonst noch etwas tun?")
    )


@ask.intent("AMAZON.StopIntent")
def ende():
    speech_text = "Danke Meister, dass ich Dir helfen durfte."
    return statement(speech_text).simple_card("Automation", speech_text)


@ask.intent("AMAZON.HelpIntent")
def help():
    speech_text = "Fuer Hilfe muss hier noch etwas getan werden."
    return statement(speech_text).simple_card("Automation", speech_text)


if __name__ == "__main__":

    app.run(host="0.0.0.0", debug=True)
