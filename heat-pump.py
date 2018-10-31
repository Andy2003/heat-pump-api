#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from time import sleep

from bindings.ElsterBinding import ElsterBinding
from bridges.MqttBridge import MqttBridge

MQTT_HOST = sys.argv[1]

binding = ElsterBinding('wpl_10_ac')
bridge = MqttBridge(MQTT_HOST, binding)

try:
    while 1:
        binding.queryForData()
        sleep(30)
finally:
    bridge.close()
