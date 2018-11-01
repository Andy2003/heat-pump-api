#!/usr/bin/python
# -*- coding: utf-8 -*-
from time import sleep

import config
from bindings.elster.ElsterBinding import ElsterBinding
from bridges.InfluxDBBridge import InfluxDBBridge
from bridges.MqttBridge import MqttBridge

binding = ElsterBinding(config.BINDING['heat_pump_id'])

try:
    if config.INFLUXDB['enabled']:
        binding.addBridge(InfluxDBBridge())
    if config.MQTT['enabled']:
        binding.addBridge(MqttBridge())

    binding.start()
    while 1:
        binding.queryForData()
        sleep(config.BINDING['update_interval'])
finally:
    binding.stop()
