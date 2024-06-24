#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This example sends random left/right commands and a constant forward command.
With the wheelchair mini-game, it would make some incremental movements.

Author: Ludovic Darmet
email: ludovic.darmet@gmail.com
"""
__author__ = "Ludovic Darmet"

import numpy as np
import time

from udp_cyb import UDPClient

# Run on localhost and default port.
client = UDPClient(ip = "localhost", port = 59075)
client.start()
time.sleep(2)
while True:
    # Start only when control and device is sent by the game
    if client.control == True:
        analogue_input_1 = np.random.normal(0, 0.5)
        # Make sure the value is between -1 and 1
        while np.abs(analogue_input_1) > 1:
            analogue_input_1 = np.random.normal(0, 0.5)
        # Send command
        client.send_command(0, 0, analogue_input_1, 0.5)
        time.sleep(1)
