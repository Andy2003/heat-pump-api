import csv


class ElsterTable(dict):
    def __init__(self, descriptor):
        super(ElsterTable, self).__init__()
        with open(descriptor) as csvfile:
            next(csvfile)
            for row in csv.reader(csvfile):
                entry = Entry(row)
                self[entry.id] = entry


class Entry:
    def __init__(self, row):
        self.topic = row[0]
        self.receiver = int(row[1], 16)
        self.id = int(row[2], 16)
        self.type = row[3]
        self.unit = row[4]

    def extractValue(self, value):
        if value is None or value == 0x8000:
            return
        if self.type == '/10':
            return float(value) / 10
        return None

    def __str__(self):
        return self.topic + ' ' + self.unit
