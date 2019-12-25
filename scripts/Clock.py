import logging
import signal
import sys
import random
import datetime
from AbstractDevice import AbstractDevice

"""
    Clock
    Publish time every 10 seconds (= 1 hour in simulation)
    Controlling :
    {'type':'order, 'order':'status'} - publish status (WARNING, IR INCREMENTS CLOCK VALUE)
    {'type':'order, 'order':'set_period', 'period':<period>, 'period_units':'s'/'m'} - to set status publication interval
"""


class Clock(AbstractDevice):

    time = {'date':None, 'hour':0}

    def __init__(self, ip="127.0.0.1", port=1883):
        # Config
        self.time['date'] = datetime.date.today()
        self.time['hour'] = 0
        super().__init__(uID=0,
                         mqtt_ip=ip,
                         mqtt_port=port,
                         name="Clock", units_name="dict",
                         base_topic="time", delay_sec=10)


    def get_address(self):
        return 0x20

    def read_data(self):
        self.time['date'] = str(datetime.date.today())
        self.time['hour'] = (self.time['hour'] + 1) % 24
        return self.time

    def message_handler(self, payload):
        pass


testSensor = None
keep_alive = True


def ctrlc_handler(signum, frame):
    global testSensor, keep_alive
    print("Ctrl+C received...")
    keep_alive = False
    testSensor.stop()

TEMPERATURE_INT_PIN = 12

# Execution or import
if __name__ == "__main__":

    logging.basicConfig(format="[%(asctime)s][%(module)s:%(funcName)s:%(lineno)d][%(levelname)s] %(message)s",
                        stream=sys.stdout)
    logging.getLogger().setLevel(logging.DEBUG)
    signal.signal(signal.SIGINT, ctrlc_handler)
    testSensor = Clock()

    while keep_alive:
        None

    print("The end")
