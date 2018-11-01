# -*- coding: utf-8 -*-
from typing import Dict, List
from typing import Set

from bindings.elster.Converter import OPERATING_MODE, DEC
from bindings.elster.Entry import SimpleEntry, ReadOnlyFormulaEntry, BaseEntry


class ElsterTable:
    entries = {
        # Boiler
        0x180: [
            SimpleEntry('hotwater/set_temperature', '°C', 0x0003, DEC),
            SimpleEntry('hotwater/set_temperature/comfort', '°C', 0x0013, DEC, True),
            SimpleEntry('hotwater/set_temperature/standby', '°C', 0x0a06, DEC, True),
            SimpleEntry('hotwater/temperature', '°C', 0x000e, DEC),
            SimpleEntry('operating_mode', '', 0x0112, OPERATING_MODE, True),
            SimpleEntry('temperature/outside', '°C', 0x000c, DEC),
        ],
        # heating unit
        0x500: [
            SimpleEntry('temperature/inverter_environment', '°C', 0x000c, DEC),

            # VD Heizen
            ReadOnlyFormulaEntry('heating/heat_output/day', 'Wh', 'A * 1000 + B', {'A': 0x092f, 'B': 0x092e}),
            ReadOnlyFormulaEntry('heating/heat_output', 'Wh', 'A * 1000000 + (B+C) * 1000', {'A': 0x0931, 'B': 0x0930, 'C': 0x092f}),

            ReadOnlyFormulaEntry('heating/energy_input/day', 'Wh', 'A * 1000 + B', {'A': 0x091f, 'B': 0x091e}),
            ReadOnlyFormulaEntry('heating/energy_input', 'Wh', 'A * 1000000 + (B+C) * 1000', {'A': 0x0921, 'B': 0x0920, 'C': 0x091f}),

            # NHZ Heizen
            ReadOnlyFormulaEntry('heating/heat_output/emergency', 'Wh', 'A * 1000000 + B * 1000 + C', {'A': 0x0929, 'B': 0x0927, 'C': 0x0926}),

            # VD Warmwasser
            ReadOnlyFormulaEntry('hotwater/heat_output/day', 'Wh', 'A * 1000 + B', {'A': 0x092b, 'B': 0x092a}),
            ReadOnlyFormulaEntry('hotwater/heat_output', 'Wh', 'A * 1000000 + (B+C) * 1000', {'A': 0x092d, 'B': 0x092c, 'C': 0x092b}),

            ReadOnlyFormulaEntry('hotwater/energy_input/day', 'Wh', 'A * 1000 + B', {'A': 0x091b, 'B': 0x091a}),
            ReadOnlyFormulaEntry('hotwater/energy_input', 'Wh', 'A * 1000000 + (B+C) * 1000', {'A': 0x091d, 'B': 0x091c, 'C': 0x091b}),

            # NHZ Warmwasser
            ReadOnlyFormulaEntry('hotwater/heat_output/emergency', 'Wh', 'A * 1000000 + B * 1000 + C', {'A': 0x0925, 'B': 0x0923, 'C': 0x0922}),
        ]

    }  # type: Dict[int, List[BaseEntry]]

    def __init__(self):
        self.ids_per_receiver = {}  # type: Dict[int, Set[int]]
        for receiver in self.entries:
            entries = set()  # type: Set[int]
            self.ids_per_receiver[receiver] = entries
            for entry in self.entries[receiver]:
                entries.update(entry.getElsterIndices())

    def topicsForUpdates(self):
        topics = []
        for entries in self.entries.values():  # type: List[BaseEntry]
            for entry in entries:
                topic = entry.getTopicForUpdates()
                if topic is not None:
                    topics.append(topic)
        return topics

    def resetValues(self):
        for entries in self.entries.values():  # type: List[BaseEntry]
            for entry in entries:
                entry.resetValues()
