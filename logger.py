#!/usr/bin/python
# -*- coding: utf-8 -*-
import time

import can

from bindings.elster.ElsterFrame import ElsterFrame


def on_can_message(msg):
    # type: (can.Message) -> None
    frame = ElsterFrame(msg=msg)
    if msg.arbitration_id in (0x180, 0x500):
        if frame.type == ElsterFrame.RESPONSE:
            print frame


# noinspection PyTypeChecker
bus = can.Bus(bustype='socketcan_native', channel='can0', receive_own_messages=False)
can.Notifier(bus, [on_can_message])

while 1:
    time.sleep(1)
