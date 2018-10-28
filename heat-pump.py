#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import can
import time
import paho.mqtt.client as mqtt

from elster.ElsterTable import ElsterTable
from elster.ElsterFrame import ElsterFrame

MQTT_HOST = sys.argv[1]
BASE_TOPIC = "heatpump/wpl_10_ac/"

# Only use one of this sender ids
# 680 - PC (ComfortSoft)
# 700 - Fremdgerät
# 780 - DCF-Modul
SENDER = 0x680

table = ElsterTable('stiebel-eltron.csv')
mqttc = mqtt.Client()


def listener(msg):
    frame = ElsterFrame(msg=msg)
    if frame.receiver != SENDER:
        # only parse messages directly send to us
        return
    e = table[frame.elsterIndex]
    if e is None:
        return
    value = e.extractValue(frame.value)
    if value is None:
        return
    mqttc.publish(BASE_TOPIC + e.topic, value)
    print BASE_TOPIC + e.topic, value, e.unit


try:
    bus = can.interface.Bus(bustype='socketcan_native', channel='can0', receive_own_messages=False)
    can.Notifier(bus, [listener])
    print "connect to:", MQTT_HOST
    mqttc.connect(MQTT_HOST)
    mqttc.loop_start()

    while 1:
        for entry in table.itervalues():
            # send a read request, the corresponding device will answer with the value
            msg = ElsterFrame(entry.receiver, entry.id, ElsterFrame.READ, None, SENDER).getCanMessage()
            bus.send(msg)
        time.sleep(30)

finally:
    mqttc.disconnect()
    mqttc.loop_stop()
