import time

import requests
from typing import Dict

from bindings.BaseBinding import BaseBinding
from bridges.BaseBridge import BaseBridge


class InfluxDBBridge(BaseBridge):

    def __init__(self, base_url, database, binding):
        # type: (str, str, BaseBinding) -> None
        super(InfluxDBBridge, self).__init__(binding)
        self.values = {}  # type: Dict[str, WrittenData]
        self.base_url = base_url
        self.database = database
        # noinspection SqlDialectInspection
        resp = requests.post(base_url + '/query', data={'q': 'CREATE DATABASE "' + database + '"'})
        if resp.status_code != 200:
            raise Exception('Cannot connect to influxdb: ' + base_url + ' -> ' + str(resp.status_code))

    def publish(self, heat_pump_id, base_topic, topic, value):
        key = base_topic + topic
        if key in self.values:
            written_data = self.values[key]
            if written_data.time_of_last_value > time.time() - 60 * 60 and written_data.last_value == value:
                return None
        else:
            written_data = WrittenData()
        written_data.time_of_last_value = time.time()
        written_data.last_value = value
        self.values[key] = written_data

        data = "heatpump,id=" + heat_pump_id + ",topic=" + topic
        if isinstance(value, (float, int)):
            data = data + " value=" + str(value)
        else:
            data = data + " str=\"" + str(value) + "\""
            print data
        requests.post(self.base_url + '/write?db=' + self.database, data=data.encode('ISO-8859-1'))


class WrittenData(object):
    __slots__ = ('last_value', 'time_of_last_value')
