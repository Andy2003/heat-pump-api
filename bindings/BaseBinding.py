from typing import List

from bridges.BaseBridge import BaseBridge


class BaseBinding(object):
    def __init__(self, heat_pump_id, topics):
        # type: (str, List[str]) -> None
        self.heat_pump_id = heat_pump_id
        self.topics = topics
        self.bridges = []  # type: List[BaseBridge]

    def onApiMessage(self, topic, payload):
        # type: (str, object) -> None
        pass

    def addBridge(self, bridge):
        # type: (BaseBridge) -> None
        bridge.binding = self
        self.bridges.append(bridge)

    def start(self):
        for bridge in self.bridges:
            bridge.start()

    def stop(self):
        for bridge in self.bridges:
            bridge.stop()
