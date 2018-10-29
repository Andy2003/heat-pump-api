import csv

OPERATING_MODE = {
    0x0000: "BUILDING_PROTECTION",
    0x0100: "STANDBY",
    0x0200: "AUTO",
    0x0300: "COMFORT",
    0x0400: "ECONOMY",
    0x0500: "HOT_WATER"
}


class ElsterTable:
    def __init__(self, descriptor):
        """

        :type descriptor: str
        """
        self.elster_entries = {}
        self.subscription_topics = {}
        with open(descriptor) as csvfile:
            next(csvfile)
            for row in csv.reader(csvfile):
                entry = Entry(row)
                self.elster_entries[entry.id] = entry
                if len(entry.subscriptionTopic) > 0:
                    self.subscription_topics[entry.subscriptionTopic] = entry

    def entries(self):
        return self.elster_entries.itervalues()

    def topics(self):
        return self.subscription_topics.iterkeys()

    def entry(self, elster_index=None, subscription_topic=None):
        # type: (int, str) -> Entry
        if elster_index is not None:
            return self.elster_entries[elster_index]
        if subscription_topic is not None:
            return self.subscription_topics[subscription_topic]


class Entry:
    def __init__(self, row):
        """

        :type row: list of str
        """
        self.publishingTopic = row[0]
        self.subscriptionTopic = row[1]
        self.receiver = int(row[2], 16)
        self.id = int(row[3], 16)
        self.type = row[4]
        self.unit = row[5]

    def extractMqttValue(self, value):
        if value is None or value == 0x8000:
            return
        if self.type == '/10':
            return float(value) / 10
        if self.type == 'operatingMode':
            operating_mode = OPERATING_MODE[value]
            if operating_mode is not None:
                return operating_mode
        return None

    def extractCanValue(self, value):
        if value is None:
            return None
        if self.type == '/10':
            # noinspection PyTypeChecker
            return int(float(value) * 10)
        if self.type == 'operatingMode':
            # noinspection PyTypeChecker
            for canId, mqttName in OPERATING_MODE.iteritems():
                if mqttName == value:
                    return canId
            return None
        return None

    def __str__(self):
        return self.publishingTopic + ' ' + self.unit
