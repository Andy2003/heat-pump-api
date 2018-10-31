from bridges.BaseBridge import BaseBridge


class BaseBinding(object):
    def __init__(self, id, topics):
        """

        :type topics: list of str
        """

        self.id = id
        self.topics = topics

    def on_message(self, topic, payload):
        # type: (str, object) -> None
        pass

    def add_bridge(self, bridge):
        # type: (BaseBridge) -> None
        pass
