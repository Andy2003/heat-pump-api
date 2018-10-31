class BaseBridge(object):
    def __init__(self, binding):
        self.binding = binding
        binding.add_bridge(self)

    def publish(self, topic, value):
        # type: (str, object) -> None
        pass
