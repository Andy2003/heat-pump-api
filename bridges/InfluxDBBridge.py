import time

import requests
from typing import Dict

import config
from bridges.BaseBridge import BaseBridge


class InfluxDBBridge(BaseBridge):

    def __init__(self):
        super(InfluxDBBridge, self).__init__()
        self.values = {}  # type: Dict[str, WrittenData]
        # noinspection SqlDialectInspection
        resp = requests.post(config.INFLUXDB['base_url'] + '/query', data={'q': 'CREATE DATABASE "' + config.INFLUXDB['database'] + '"'})
        if resp.status_code != 200:
            raise Exception('Cannot connect to influxdb: ' + config.INFLUXDB['base_url'] + ' -> ' + str(resp.status_code))

    def publishApiMessage(self, heat_pump_id, base_topic, topic, value):
        key = base_topic + topic
        if key in self.values:
            written_data = self.values[key]
            if written_data.time_of_last_value > time.time() - config.INFLUXDB['write_through_time'] and written_data.last_value == value:
                return None
        else:
            written_data = WrittenData()
        written_data.time_of_last_value = time.time()
        written_data.last_value = value
        self.values[key] = written_data

        data = config.INFLUXDB['measurement'] + ",id=" + heat_pump_id + ",topic=" + topic
        if isinstance(value, (float, int)):
            data = data + " value=" + str(value)
        else:
            data = data + " str=\"" + str(value) + "\""
            print data
        requests.post(config.INFLUXDB['base_url'] + '/write?db=' + config.INFLUXDB['database'], data=data.encode('ISO-8859-1'))


class WrittenData(object):
    __slots__ = ('last_value', 'time_of_last_value')
