from paho.mqtt.client import Client as MqttClient, MQTTMessage

from bindings.BaseBinding import BaseBinding
from bridges.BaseBridge import BaseBridge


class MqttBridge(BaseBridge):

    def __init__(self, host, binding):
        # type: (str, BaseBinding) -> None
        super(MqttBridge, self).__init__(binding)

        print "mqtt connect to:", host
        self.client = MqttClient()
        self.client.on_message = self.onMqttMessage
        self.client.on_connect = self.onConnect
        self.client.connect(host)
        self.client.loop_start()

    def publishApiMessage(self, heat_pump_id, base_topic, topic, value):
        self.client.publish(base_topic + topic, value)

    # noinspection PyUnusedLocal
    def onConnect(self, client, userdata, flags, rc):
        # type: (MqttBridge, MqttClient, object, dict, object) -> None
        topics = []
        for topic in self.binding.topics:
            topics.append((topic, 0))
        if len(topics) == 0:
            return
        print "mqtt subscribing to topics: ", topics
        client.subscribe(topics)

    # noinspection PyUnusedLocal
    def onMqttMessage(self, client, userdata, msg):
        # type: (MqttBridge, MqttClient, object, MQTTMessage) -> None
        topic = str(msg.topic)
        self.binding.onApiMessage(topic, msg.payload)

    def close(self):
        self.client.disconnect()
        self.client.loop_stop()
