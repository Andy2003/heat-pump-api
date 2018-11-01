class BaseBridge(object):
    def __init__(self):
        self.binding = None

    def publishApiMessage(self, id, base_topic, topic, value):
        # type: (str, str, str, object) -> None
        pass

    def start(self):
        pass

    def stop(self):
        pass
