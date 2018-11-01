# -*- coding: utf-8 -*-
import re

from typing import Dict, List
from typing import Set

VARIABLES_PATTERN = re.compile('(?:(?:;\s*)?([A-Za-z]+?)=(0x[\da-fA-F]{4}))')


class Converter(object):
    def extractCanValue(self, value):
        pass

    def extractApiValue(self, value):
        pass


class FactorConverter(Converter):
    def __init__(self, can_to_api_factor):
        self.can_to_api_factor = can_to_api_factor

    def extractCanValue(self, value):
        return int(float(value) / self.can_to_api_factor)

    def extractApiValue(self, value):
        return int(float(value) * self.can_to_api_factor)


class BaseEntry(object):
    def __init__(self, publishing_topic, unit):
        # type: (str, str) -> None
        self.unit = unit
        self.publishing_topic = publishing_topic

    def getElsterIndices(self):
        # type: () -> List[int]
        pass

    def getUpdateEvent(self, elster_index, value):
        # type: (int, object) -> (BaseEntry, object)
        pass

    def resetValues(self):
        pass

    def canBeUpdatedByTopic(self, topic):
        # type: (str) -> bool
        return False

    def extractCanValue(self, payload):
        pass

    def getTopicForUpdates(self):
        pass


class ReadOnlyFormulaEntry(BaseEntry):

    def __init__(self, publishing_topic, unit, formula, variables):
        # type: (str, str,str, Dict[str, int]) -> None
        super(ReadOnlyFormulaEntry, self).__init__(publishing_topic, unit)
        self.formula = formula
        self.variables = variables
        self.values = {}  # type: Dict[str, object]

    def getElsterIndices(self):
        return self.variables.itervalues()

    def getUpdateEvent(self, elster_index, value):
        # noinspection PyTypeChecker
        for (variable, elstid) in self.variables.iteritems():
            if elstid == elster_index:
                self.values[variable] = value
                break
        if len(self.values) == len(self.variables):
            return self, (eval(self.formula, {}, self.values))
        return None

    def resetValues(self):
        self.values.clear()


class SimpleEntry(BaseEntry):
    def __init__(self, publishing_topic, unit, elster_index, converter, updatable=False):
        # type: (str,str, int, Converter, bool) -> None
        super(SimpleEntry, self).__init__(publishing_topic, unit)
        self.elster_index = elster_index
        self.converter = converter
        self.updatable = updatable

    def getElsterIndices(self):
        return [self.elster_index]

    def getUpdateEvent(self, elster_index, value):
        if self.elster_index != elster_index:
            return None
        api_value = self.converter.extractApiValue(value)
        if api_value is not None:
            return self, api_value

    def extractCanValue(self, payload):
        return self.converter.extractCanValue(payload)

    def getTopicForUpdates(self):
        if not self.updatable:
            return None
        return self.publishing_topic + '/update'

    def canBeUpdatedByTopic(self, topic):
        return self.getTopicForUpdates() == topic


class OperatingMode(Converter):
    OPERATING_MODE = {
        0x0000: "BUILDING_PROTECTION",
        0x0100: "STANDBY",
        0x0200: "AUTO",
        0x0300: "COMFORT",
        0x0400: "ECONOMY",
        0x0500: "HOT_WATER"
    }

    def extractCanValue(self, value):
        # noinspection PyTypeChecker
        for canId, apiName in self.OPERATING_MODE.iteritems():
            if apiName == value:
                return canId

    def extractApiValue(self, value):
        operating_mode = self.OPERATING_MODE[value]
        if operating_mode is not None:
            return operating_mode


dec = FactorConverter(0.1)


class ElsterTable:
    _entries = {
        # Boiler
        0x180: [
            SimpleEntry('hotwater/set_temperature', '°C', 0x0003, dec),
            SimpleEntry('hotwater/set_temperature/comfort', '°C', 0x0013, dec, True),
            SimpleEntry('hotwater/set_temperature/standby', '°C', 0x0a06, dec, True),
            SimpleEntry('hotwater/temperature', '°C', 0x000e, dec),
            SimpleEntry('operating_mode', '', 0x0112, OperatingMode(), True),
        ],
        # heating unit
        0x500: [
            ReadOnlyFormulaEntry('heating/energy/day', 'Wh', 'x * 1000 + y', {'x': 0x092f, 'y': 0x092e}),
            ReadOnlyFormulaEntry('heating/energy', 'Wh', 'A * 1000000 + (B+C) * 1000 + D',
                                 {'A': 0x0931, 'B': 0x0930, 'C': 0x092f, 'D': 0x092e}),
        ]

    }  # type: Dict[int, List[BaseEntry]]

    def __init__(self):
        self.ids_per_receiver = {}  # type: Dict[int, Set[int]]
        for receiver in self._entries:
            entries = set()  # type: Set[int]
            self.ids_per_receiver[receiver] = entries
            for entry in self._entries[receiver]:
                entries.update(entry.getElsterIndices())

    def topicsForUpdates(self):
        topics = []
        # noinspection PyTypeChecker
        for entries in self._entries.itervalues():  # type: List[BaseEntry]
            for entry in entries:
                topic = entry.getTopicForUpdates()
                if topic is not None:
                    topics.append(topic)
        return topics

    def getApiUpdateEvents(self, sender, elster_index, value):
        # type: (int, int, object) -> List[(BaseEntry, object)]
        if sender not in self._entries:
            return []
        entries = self._entries[sender]
        updates = []
        for entry in entries:
            update_event = entry.getUpdateEvent(elster_index, value)
            if update_event is not None:
                updates.append(update_event)
        return updates

    def getCanUpdateEvents(self, topic, payload):
        # type: (str, object) -> List[(int, int, int)]
        result = []
        # noinspection PyTypeChecker
        for (receiver, entries) in self._entries.iteritems():
            for entry in entries:  # type: BaseEntry
                if entry.canBeUpdatedByTopic(topic):
                    can_value = entry.extractCanValue(payload)
                    if isinstance(can_value, int):
                        result.append((receiver, entry.getElsterIndices()[0], can_value))
        return result

    def resetValues(self):
        # noinspection PyTypeChecker
        for entries in self._entries.itervalues():  # type: List[BaseEntry]
            for entry in entries:
                entry.resetValues()
