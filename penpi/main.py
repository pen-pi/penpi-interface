#!/usr/bin/env python3

import logging
from threading import Thread

from penpi.screen import Screen
from penpi.gatt.server import GattServer
from penpi.gatt.advertise import GattAdvertise



class Main():
    def run():
        logging.basicConfig(level=logging.INFO, format='%(relativeCreated)6d %(threadName)s %(message)s')
        
        thread_screen = Thread(target = Screen.run)
        thread_server = Thread(target = GattServer.run)
        thread_advertise = Thread(target = GattAdvertise.run)
        
        thread_screen.start()
        thread_server.start()
        thread_advertise.start()

        thread_advertise.join()
        thread_server.join()
        thread_screen.join()
