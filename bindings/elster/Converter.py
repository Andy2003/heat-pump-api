class Converter(object):

    def convertApiToCan(self, value):
        # type: (object) -> int
        pass

    def convertCanToApi(self, value):
        # type: (int) -> object
        pass


class FactorConverter(Converter):
    def __init__(self, can_to_api_factor):
        self.can_to_api_factor = can_to_api_factor

    def convertApiToCan(self, value):
        # type: (object) -> int
        # noinspection PyTypeChecker
        return int(float(value) / self.can_to_api_factor)

    def convertCanToApi(self, value):
        # type: (int) -> object
        # noinspection PyTypeChecker
        return float(value) * self.can_to_api_factor


class OperatingMode(Converter):
    MODES = {
        0x0000: "BUILDING_PROTECTION",
        0x0100: "STANDBY",
        0x0200: "AUTO",
        0x0300: "COMFORT",
        0x0400: "ECONOMY",
        0x0500: "HOT_WATER"
    }

    def convertApiToCan(self, value):
        # noinspection PyTypeChecker
        for canId, apiName in self.MODES.iteritems():
            if apiName == value:
                return canId

    def convertCanToApi(self, value):
        operating_mode = self.MODES[value]
        if operating_mode is not None:
            return operating_mode


OPERATING_MODE = OperatingMode()
ONE = FactorConverter(1)
DEC = FactorConverter(0.1)
CENT = FactorConverter(0.01)
