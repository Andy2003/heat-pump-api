import ctypes

from can import Message


class ElsterFrame(object):
    WRITE = 0x0
    READ = 0x1
    RESPONSE = 0x2
    ACK = 0x3
    WRITE_ACK = 0x4
    WRITE_RESPONSE = 0x5
    SYSTEM = 0x6
    SYSTEM_RESPONSE = 0x7
    WRITE_LARGE = 0x20
    READ_LARGE = 0x21

    __slots__ = (
        "sender",
        "receiver",
        "type",
        "elster_index",
        "value"
    )

    def __init__(self, receiver=None, elster_index=None, message_type=None, value=None, sender=0x680, msg=None, ):
        # type: (int, int, int, int, int, Message) -> None
        if msg is not None:
            self.readCanMessage(msg)
        else:
            self.sender = sender
            self.receiver = receiver
            self.type = message_type
            self.elster_index = elster_index
            self.value = value

    def readCanMessage(self, msg):
        # type: (Message) -> None
        self.sender = msg.arbitration_id
        data = msg.data
        self.receiver = (data[0] & 0xf0) * 8 + (data[1] & 0x0f)
        self.type = data[0] & 0x0f
        if data[2] == 0xFA:
            # extension telegram
            self.elster_index = ((data[3] & 0xFF) << 8) | (data[4] & 0xFF)
            if len(data) == 7:
                self.value = ctypes.c_int16(((data[5] & 0xFF) << 8) | (data[6] & 0xFF)).value
        else:
            self.elster_index = data[2]
            if len(data) >= 5:
                self.value = ctypes.c_int16(((data[3] & 0xFF) << 8) | (data[4] & 0xFF)).value

    def __str__(self):
        return "ElsterFrame [%04x -> %04x] %04x: %d (%s)" % (
            self.sender, self.receiver, self.elster_index, self.value, self.type
        )

    def getCanMessage(self):
        # type: () -> Message
        assert self.receiver <= 0x7ff
        if self.type == ElsterFrame.READ:
            data = [0] * 5
        else:
            data = [0] * 7

        data[0] = (self.type & 0xf) | ((self.receiver >> 3) & 0xf0)
        data[1] = self.receiver & 0x7f
        data[2] = 0xfa
        data[3] = self.elster_index >> 8
        data[4] = self.elster_index & 0xff
        if self.value is not None and self.type == ElsterFrame.WRITE:
            data[5] = ctypes.c_ubyte(self.value >> 8).value
            data[6] = ctypes.c_ubyte(self.value & 0xff).value
        return Message(arbitration_id=self.sender,
                       data=data,
                       extended_id=False)
