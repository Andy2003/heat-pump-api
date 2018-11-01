from typing import List, Dict

from bindings.elster.Converter import Converter


class BaseEntry(object):
    def __init__(self, publishing_topic, unit):
        # type: (str, str) -> None
        self.unit = unit
        self.publishing_topic = publishing_topic

    def getElsterIndices(self):
        # type: () -> List[int]
        pass

    def parseCanValue(self, elster_index, value):
        # type: (int, int) -> object
        pass

    def resetValues(self):
        pass

    def convertApiValueToCan(self, api_value):
        # type: (object) -> int
        pass

    def getTopicForUpdates(self):
        pass

    def isUpdatableByTopic(self, topic):
        # type: (str) -> bool
        return False


class ReadOnlyFormulaEntry(BaseEntry):

    def __init__(self, publishing_topic, unit, formula, variables):
        # type: (str, str,str, Dict[str, int]) -> None
        super(ReadOnlyFormulaEntry, self).__init__(publishing_topic, unit)
        self.formula = formula
        self.variables = variables
        self.values = {}  # type: Dict[str, object]

    def getElsterIndices(self):
        return self.variables.itervalues()

    def parseCanValue(self, elster_index, value):
        # type: (int, int) -> object
        changed = False
        # noinspection PyTypeChecker
        for (variable, elstid) in self.variables.iteritems():
            if elstid == elster_index:
                self.values[variable] = value
                changed = True
                break
        if changed and len(self.values) == len(self.variables):
            return eval(self.formula, {}, self.values)
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

    def parseCanValue(self, elster_index, value):
        if self.elster_index != elster_index:
            return None
        api_value = self.converter.convertCanToApi(value)
        if api_value is not None:
            return api_value

    def convertApiValueToCan(self, api_value):
        return self.converter.convertApiToCan(api_value)

    def getTopicForUpdates(self):
        if not self.updatable:
            return None
        return self.publishing_topic + '/update'

    def isUpdatableByTopic(self, topic):
        return self.getTopicForUpdates() == topic
