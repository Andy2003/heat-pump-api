from typing import List

from bridges.BaseBridge import BaseBridge


class BaseBinding(object):
    def __init__(self, heat_pump_id, topics):
        # type: (str, List[str]) -> None
        self.heat_pump_id = heat_pump_id
        self.topics = topics

    def on_api_message(self, topic, payload):
        # type: (str, object) -> None
        pass

    def add_bridge(self, bridge):
        # type: (BaseBridge) -> None
        pass
