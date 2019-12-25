# Sys utils
import logging
import signal
import sys

from TestSensor import TestSensor

"""
    Test senor is just posting value of 100 +- 5 to a topic /test_device/data
    The serverr is localhost with port 1883 (Can't be changed)
    It is responsive to orders given to uID 0 or all to a topic /test_device/orders
    Controlling :
    {'type':'order, 'order':'status'} - publish status
    {'type':'order, 'order':'set_period', 'period':<period>, 'period_units':'s'/'m'} - to set status publication interval
"""

testSensor = None
keep_alive = True

IP = "127.0.0.1"
PORT = 1883

def ctrlc_handler(signum, frame):
    global testSensor, keep_alive
    if testSensor is not None:
        testSensor.stop()
        testSensor = None
    keep_alive = False

def main() :
    global clock, temperature, luminosity, shutter, lamp, presence, keep_alive
    # SETTING LOGGER
    logging.basicConfig(format="[%(asctime)s][%(module)s:%(funcName)s:%(lineno)d][%(levelname)s] %(message)s",
                        stream=sys.stdout)
    logging.getLogger().setLevel(logging.DEBUG)
    # SETTING INTERRUPTER
    signal.signal(signal.SIGINT, ctrlc_handler)

    clock = TestSensor()

    while keep_alive:
        None

    print("The end")

if __name__ == '__main__':
    main()