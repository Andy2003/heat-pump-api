class BaseBridge(object):
    def __init__(self, binding):
        self.binding = binding
        binding.addBridge(self)

    def publishApiMessage(self, id, base_topic, topic, value):
        # type: (str, str, str, object) -> None
        pass
