class BaseBridge(object):
    def __init__(self, binding):
        self.binding = binding
        binding.add_bridge(self)

    def publish(self, id, base_topic, topic, value):
        # type: (str, str, str, object) -> None
        pass
