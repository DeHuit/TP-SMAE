import logging
import signal
import sys
import random

from AbstractDevice import AbstractDevice

"""
    Test senor is just posting value of 100 +- 5 to a topic /test_device/data
    It is responsive to orders given to uID 0 or all to a topic /test_device/orders
    Controlling :
    {'type':'order, 'order':'status'} - publish status
    {'type':'order, 'order':'set_period', 'period':<period>, 'period_units':'s'/'m'} - to set status publication interval
"""

class TestSensor(AbstractDevice):

    base = 100

    def __init__(self):
        # Config
        self.base = 100
        super().__init__(uID=0, name="test device", units_name="something",
                         base_topic="/test_device", delay_sec=10)


    def get_address(self):
        return 0x20

    def read_data(self):
        return self.base + random.randint(-5, 5)


    def message_handler(self, payload):
        print(" I have message with unknown content : " + str(payload))

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
    testSensor = TestSensor()

    while keep_alive:
        None

    print("The end")
