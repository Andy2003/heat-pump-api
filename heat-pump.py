#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from time import sleep

from bindings.ElsterBinding import ElsterBinding
from bridges.MqttBridge import MqttBridge

MQTT_HOST = sys.argv[1]
INFLUX_DB_URL = sys.argv[2]

binding = ElsterBinding('wpl_10_ac')
# InfluxDBBridge(INFLUX_DB_URL, 'heatpump', binding)
bridge = MqttBridge(MQTT_HOST, binding)

try:
    while 1:
        binding.queryForData()
        sleep(30)
finally:
    bridge.close()
