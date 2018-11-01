# -*- coding: utf-8 -*-
import time

import can
from can import Message
from typing import List

from bindings.BaseBinding import BaseBinding
from bindings.elster.ElsterFrame import ElsterFrame
from bindings.elster.ElsterTable import ElsterTable, BaseEntry
from bridges.BaseBridge import BaseBridge


class ElsterBinding(BaseBinding):
    # Only use one of this sender ids
    # 680 - PC (ComfortSoft)
    # 700 - Fremdgerät
    # 780 - DCF-Modul
    SENDER = 0x680

    def __init__(self, heat_pump_id):
        self.table = ElsterTable()

        self.base_topic = 'heatpump/' + heat_pump_id + '/'
        self.bridges = []  # type: List[BaseBridge]

        # noinspection PyTypeChecker
        self.bus = can.Bus(bustype='socketcan_native', channel='can0', receive_own_messages=False)
        can.Notifier(self.bus, [self.on_can_message])

        topics = []
        for topic in self.table.topicsForUpdates():
            topics.append(self.base_topic + topic)

        super(ElsterBinding, self).__init__(heat_pump_id, topics)

    def on_api_message(self, topic, payload):
        # type: (str, object) -> None
        print "API message ", topic, ": ", payload
        if not str.startswith(topic, self.base_topic):
            return
        topic = str.replace(topic, self.base_topic, '')
        updateEvents = self.table.getCanUpdateEvents(topic, payload)
        if len(updateEvents) == 0:
            return
        for event in updateEvents:
            frame = ElsterFrame(sender=ElsterBinding.SENDER, receiver=event[0], elster_index=event[1],
                                message_type=ElsterFrame.WRITE, value=event[2])
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
        updates = self.table.getApiUpdateEvents(msg.arbitration_id, frame.elster_index, frame.value)
        if updates is None:
            return
        for update in updates:
            entry = update[0]  # type: BaseEntry
            value = update[1]
            topic = self.base_topic + entry.publishing_topic
            print topic, value, entry.unit
            for bridge in self.bridges:
                bridge.publish(self.heat_pump_id, self.base_topic, entry.publishing_topic, value)

    def queryForData(self):
        self.table.resetValues()

        # noinspection PyTypeChecker
        for (receiver, entries) in self.table.ids_per_receiver.iteritems():
            for entry in entries:
                # send a read request, the corresponding device will answer with the value
                frame = ElsterFrame(sender=ElsterBinding.SENDER, receiver=receiver, elster_index=entry,
                                    message_type=ElsterFrame.READ)
                self.bus.send(frame.getCanMessage())
                time.sleep(0.1)
