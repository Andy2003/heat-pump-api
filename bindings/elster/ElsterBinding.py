# -*- coding: utf-8 -*-
import time

import can
from can import Message
from typing import Dict, List
from typing import Set

import config
from bindings.BaseBinding import BaseBinding
from bindings.elster.Converter import DEC, CENT, OPERATING_MODE
from bindings.elster.ElsterFrame import ElsterFrame
from bindings.elster.Entry import SimpleEntry, BaseEntry, ReadOnlyFormulaEntry


class ElsterBinding(BaseBinding):
    # Only use one of this sender ids
    # 680 - PC (ComfortSoft)
    # 700 - Fremdgerät
    # 780 - DCF-Modul
    SENDER = 0x680

    ENTRIES = {
        # Boiler
        0x180: [
            SimpleEntry('boiler/hotwater/set_temperature', '°C', 0x0003, DEC),
            SimpleEntry('boiler/hotwater/set_temperature/comfort', '°C', 0x0013, DEC, True),
            SimpleEntry('boiler/hotwater/set_temperature/standby', '°C', 0x0a06, DEC, True),
            SimpleEntry('boiler/hotwater/temperature', '°C', 0x000e, DEC),
            SimpleEntry('operating_mode', '', 0x0112, OPERATING_MODE, True),

            SimpleEntry('outside/environment/temperature', '°C', 0x000c, DEC),

            # Heizkreis-Isttemperatur Heizkreis 1
            SimpleEntry('heating_circuit1/heating/temperature', '°C', 0x02ca, DEC),
            # Heizkreis-Solltemperatur Heizkreis 1 (HK1) bei Festwertregelung wird Festwerttemperatur angezeigt.
            SimpleEntry('heating_circuit1/heating/set_temperature', '°C', 0x01d7, DEC),
            # Nachheizstufen-Vorlauf-Isttemperatur
            SimpleEntry('booster/flow_temperature', '°C', 0x06a0, DEC),
            # RÜCKLAUFISTTEMPERATUR WP
            SimpleEntry('heatpump/heating/return_temperature', '°C', 0x0016, DEC),
            # Pufferspeicher-Isttemperatur
            SimpleEntry('buffer/heating/temperature', '°C', 0x0078, DEC),
            # Pufferspeicher-Solltemperatur
            SimpleEntry('buffer/heating/set_temperature', '°C', 0x01d5, DEC),
            # HEIZUNGSDRUCK
            SimpleEntry('heating/pressure', 'bar', 0x0674, CENT),
            # VOLUMENSTROM
            # SimpleEntry('heating/volumetric_flow_rate', 'l/min', 0x0673, CENT),
            # SimpleEntry('system/hotwater/volumetric_flow_rate', 'l/min', 0x0673, CENT),
            # ANLAGENFROST
            # SimpleEntry('system/freeze_temperature', '°C', 0x0a00, DEC),

            SimpleEntry('heatpump/heating/bivalence_temperatur', '°C', 0x01ac, DEC),
            SimpleEntry('heatpump/heating/limit_of_use_temperatur', '°C', 0x01ae, DEC),

            SimpleEntry('heatpump/hotwater/bivalence_temperatur', '°C', 0x01ad, DEC),
            SimpleEntry('heatpump/hotwater/limit_of_use_temperatur', '°C', 0x01af, DEC),
        ],
        # heating unit
        0x500: [
            SimpleEntry('inverter/environment/temperature', '°C', 0x000c, DEC),

            # VD Heizen
            ReadOnlyFormulaEntry('compressor/heating/heat_output/day', 'Wh', 'A * 1000 + B', {'A': 0x092f, 'B': 0x092e}),
            ReadOnlyFormulaEntry('compressor/heating/heat_output', 'Wh', 'A * 1000000 + (B+C) * 1000', {'A': 0x0931, 'B': 0x0930, 'C': 0x092f}),

            ReadOnlyFormulaEntry('compressor/heating/energy_input/day', 'Wh', 'A * 1000 + B', {'A': 0x091f, 'B': 0x091e}),
            ReadOnlyFormulaEntry('compressor/heating/energy_input', 'Wh', 'A * 1000000 + (B+C) * 1000', {'A': 0x0921, 'B': 0x0920, 'C': 0x091f}),

            # NHZ Heizen
            ReadOnlyFormulaEntry('booster/heating/heat_output', 'Wh', 'A * 1000000 + B * 1000 + C', {'A': 0x0929, 'B': 0x0927, 'C': 0x0926}),

            # VD Warmwasser
            ReadOnlyFormulaEntry('compressor/hotwater/heat_output/day', 'Wh', 'A * 1000 + B', {'A': 0x092b, 'B': 0x092a}),
            ReadOnlyFormulaEntry('compressor/hotwater/heat_output', 'Wh', 'A * 1000000 + (B+C) * 1000', {'A': 0x092d, 'B': 0x092c, 'C': 0x092b}),

            ReadOnlyFormulaEntry('compressor/hotwater/energy_input/day', 'Wh', 'A * 1000 + B', {'A': 0x091b, 'B': 0x091a}),
            ReadOnlyFormulaEntry('compressor/hotwater/energy_input', 'Wh', 'A * 1000000 + (B+C) * 1000', {'A': 0x091d, 'B': 0x091c, 'C': 0x091b}),

            # NHZ Warmwasser
            ReadOnlyFormulaEntry('booster/hotwater/heat_output', 'Wh', 'A * 1000000 + B * 1000 + C', {'A': 0x0925, 'B': 0x0923, 'C': 0x0922}),
        ]

    }  # type: Dict[int, List[BaseEntry]]

    def __init__(self, heat_pump_id):
        topics = []
        self.base_topic = 'heatpump/' + heat_pump_id + '/'
        self.ids_per_receiver = {}  # type: Dict[int, Set[int]]

        for receiver, entries in self.ENTRIES.items():
            elster_ids = set()  # type: Set[int]
            self.ids_per_receiver[receiver] = elster_ids
            for entry in entries:
                elster_ids.update(entry.getElsterIndices())
                topic = entry.getTopicForUpdates()
                if topic is not None:
                    topics.append(self.base_topic + topic)

        super(ElsterBinding, self).__init__(heat_pump_id, topics)

        # noinspection PyTypeChecker
        self.bus = can.Bus(bustype='socketcan_native', channel='can0', receive_own_messages=False)
        can.Notifier(self.bus, [self.onCanMessage])

    def onApiMessage(self, topic, payload):
        # type: (str, object) -> None
        print "API message ", topic, ": ", payload
        if not str.startswith(topic, self.base_topic):
            return
        topic = str.replace(topic, self.base_topic, '')

        for receiver, entries in self.ENTRIES.items():
            for entry in entries:  # type: BaseEntry
                if entry.isUpdatableByTopic(topic):
                    can_value = entry.convertApiValueToCan(payload)
                    if isinstance(can_value, int):
                        frame = ElsterFrame(sender=ElsterBinding.SENDER, receiver=receiver, elster_index=entry.getElsterIndices()[0],
                                            message_type=ElsterFrame.WRITE, value=can_value)
                        print frame
                        self.bus.send(frame.getCanMessage())

    def onCanMessage(self, msg):
        # type: (Message) -> None
        frame = ElsterFrame(msg=msg)
        if config.BINDING['handle_all_messages'] is False and frame.receiver != ElsterBinding.SENDER:
            # only parse messages directly send to us
            return
        if msg.arbitration_id not in self.ENTRIES:
            return
        for entry in self.ENTRIES[msg.arbitration_id]:
            can_value = entry.parseCanValue(frame.elster_index, frame.value)
            if can_value is not None:
                topic = self.base_topic + entry.publishing_topic
                print topic, can_value, entry.unit
                for bridge in self.bridges:
                    bridge.publishApiMessage(self.heat_pump_id, self.base_topic, entry.publishing_topic, can_value)

    def resetValues(self):
        for entries in self.ENTRIES.values():  # type: List[BaseEntry]
            for entry in entries:
                entry.resetValues()

    def queryForData(self):
        self.resetValues()

        for (receiver, entries) in self.ids_per_receiver.items():
            for entry in entries:
                # send a read request, the corresponding device will answer with the value
                frame = ElsterFrame(sender=ElsterBinding.SENDER, receiver=receiver, elster_index=entry, message_type=ElsterFrame.READ)
                self.bus.send(frame.getCanMessage())
                time.sleep(0.01)
