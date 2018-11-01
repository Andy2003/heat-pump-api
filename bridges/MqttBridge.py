from paho.mqtt.client import Client as MqttClient, MQTTMessage

from bindings.BaseBinding import BaseBinding
from bridges.BaseBridge import BaseBridge


class MqttBridge(BaseBridge):

    def __init__(self, host, binding):
        # type: (str, BaseBinding) -> None
        super(MqttBridge, self).__init__(binding)

        print "mqtt connect to:", host
        self.client = MqttClient()
        self.client.on_message = self.listener
        self.client.on_connect = self.on_connect
        self.client.connect(host)
        self.client.loop_start()

    def publish(self, heat_pump_id, base_topic, topic, value):
        self.client.publish(base_topic + topic, value)

    # noinspection PyUnusedLocal
    def on_connect(self, client, userdata, flags, rc):
        # type: (MqttBridge, MqttClient, object, dict, object) -> None
        topics = []
        for topic in self.binding.topics:
            topics.append((topic, 0))
        print "mqtt subscribing to topics: ", topics
        client.subscribe(topics)

    # noinspection PyUnusedLocal
    def listener(self, client, userdata, msg):
        # type: (MqttBridge, MqttClient, object, MQTTMessage) -> None
        topic = str(msg.topic)
        self.binding.on_api_message(topic, msg.payload)

    def close(self):
        self.client.disconnect()
        self.client.loop_stop()
