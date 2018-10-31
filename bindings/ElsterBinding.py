# -*- coding: utf-8 -*-
import os

import can
from can import Message

from bindings.BaseBinding import BaseBinding
from bindings.elster.ElsterFrame import ElsterFrame
from bindings.elster.ElsterTable import ElsterTable


class ElsterBinding(BaseBinding):
    # Only use one of this sender ids
    # 680 - PC (ComfortSoft)
    # 700 - Fremdgerät
    # 780 - DCF-Modul
    SENDER = 0x680

    def __init__(self, id):
        file = os.path.join(os.path.dirname(__file__), 'stiebel-eltron.csv')
        self.table = ElsterTable(file)

        self.base_topic = 'heatpump/' + id + '/'
        self.bridges = []

        # noinspection PyTypeChecker
        self.bus = can.Bus(bustype='socketcan_native', channel='can0', receive_own_messages=False)
        can.Notifier(self.bus, [self.on_can_message])

        topics = []
        for topic in self.table.topics():
            topics.append(self.base_topic + topic)

        super(ElsterBinding, self).__init__(id, topics)

    def on_message(self, topic, payload):
        # type: (str, object) -> None
        if not str.startswith(topic, self.base_topic):
            return
        topic = str.replace(topic, self.base_topic, '')
        entry = self.table.entry(subscription_topic=topic)
        if entry is None:
            return
        value = entry.extractCanValue(payload)
        if value is None:
            return
        frame = ElsterFrame(sender=ElsterBinding.SENDER, receiver=entry.receiver, elster_index=entry.id,
                            message_type=ElsterFrame.WRITE, value=value)
        print frame
        self.bus.send(frame.getCanMessage())

    def add_bridge(self, bridge):
        self.bridges.append(bridge)

    def on_can_message(self, msg):
        # type: (Message) -> None
        frame = ElsterFrame(msg=msg)
        if frame.receiver != ElsterBinding.SENDER:
            # only parse messages directly send to us
            return
        entry = self.table.entry(elster_index=frame.elster_index)
        if entry is None:
            return
        value = entry.extractApiValue(frame.value)
        if value is None:
            return
        topic = self.base_topic + entry.publishingTopic
        print topic, value, entry.unit
        for bridge in self.bridges:
            bridge.publish(topic, value)

    def queryForData(self):
        for entry in self.table.entries():
            # send a read request, the corresponding device will answer with the value
            frame = ElsterFrame(sender=ElsterBinding.SENDER, receiver=entry.receiver, elster_index=entry.id,
                                message_type=ElsterFrame.READ)
            self.bus.send(frame.getCanMessage())
