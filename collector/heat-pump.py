#!/usr/bin/python
# -*- coding: utf-8 -*-
from sys import argv
from time import sleep

from can import Notifier, Bus as CanBus, Message
from paho.mqtt.client import Client as MqttClient, MQTTMessage

from elster.ElsterFrame import ElsterFrame
from elster.ElsterTable import ElsterTable

MQTT_HOST = argv[1]
BASE_TOPIC = "heatpump/wpl_10_ac/"

# Only use one of this sender ids
# 680 - PC (ComfortSoft)
# 700 - Fremdgerät
# 780 - DCF-Modul
SENDER = 0x680

table = ElsterTable('stiebel-eltron.csv')
mqttc = MqttClient()


def canListener(msg):
    # type: (Message) -> None

    frame = ElsterFrame(msg=msg)
    if frame.receiver != SENDER:
        # only parse messages directly send to us
        return
    entry = table.entry(elster_index=frame.elster_index)
    if entry is None:
        return
    value = entry.extractMqttValue(frame.value)
    if value is None:
        return
    mqttc.publish(BASE_TOPIC + entry.publishingTopic, value)
    print BASE_TOPIC + entry.publishingTopic, value, entry.unit


# noinspection PyUnusedLocal
def mqttListener(client, userdata, msg):
    # type: (MqttClient, object, MQTTMessage) -> None
    topic = str(msg.topic)
    if not str.startswith(topic, BASE_TOPIC):
        return
    topic = str.replace(topic, BASE_TOPIC, '')
    entry = table.entry(subscription_topic=topic)
    if entry is None:
        return
    value = entry.extractCanValue(msg.payload)
    if value is None:
        return
    frame = ElsterFrame(sender=SENDER, receiver=entry.receiver, elster_index=entry.id,
                        message_type=ElsterFrame.WRITE, value=value)
    print frame
    bus.send(frame.getCanMessage())


# noinspection PyUnusedLocal
def on_connect(client, userdata, flags, rc):
    topics = []
    for topic in table.topics():
        topics.append((BASE_TOPIC + topic, 0))
    print "subscribe to", topics
    client.subscribe(topics)


def queryForData():
    for entry in table.entries():
        # send a read request, the corresponding device will answer with the value
        frame = ElsterFrame(sender=SENDER, receiver=entry.receiver, elster_index=entry.id,
                            message_type=ElsterFrame.READ)
        bus.send(frame.getCanMessage())


try:
    # noinspection PyTypeChecker
    bus = CanBus(bustype='socketcan_native', channel='can0', receive_own_messages=False)
    Notifier(bus, [canListener])

    print "connect to:", MQTT_HOST
    mqttc.on_message = mqttListener
    mqttc.on_connect = on_connect
    mqttc.connect(MQTT_HOST)
    mqttc.loop_start()

    while 1:
        queryForData()
        sleep(30)

finally:
    mqttc.disconnect()
    mqttc.loop_stop()
