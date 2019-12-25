import logging
import signal
import sys
from AbstractDevice import AbstractDevice
# I2C
import board
import busio
import adafruit_tsl2561

"""
    Luminosity sensor
    Publish perceived luminosity
    Controlling :
    {'type':'order', 'order':'status'} - publish status
    {'type':'order', 'order':'set_period', 'period':<period>, 'period_units':'s'/'m'} - to set status publication interval
"""


class LuminositySensor(AbstractDevice):
    # Private data
    i2c_address = 0x39
    sensor = None

    def get_address(self):
        return self.i2c_address

    def __init__(self, i2c_address=0x39,
                 name="luminosity_sensor",
                 base_topic="/1R1/014/luminosity", delay_sec=60,
                 mqtt_ip="127.0.0.1", mqtt_port="1883"):
        # Create instance
        self.i2c_address = i2c_address
        i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = adafruit_tsl2561.TSL2561(i2c, address=self.i2c_address)
        # Call father's constructor method
        super().__init__(self, name=name, units_name="lux",
                         base_topic=base_topic, delay_sec=delay_sec,
                         mqtt_ip=mqtt_ip, mqtt_port=mqtt_port)

    def read_data(self):
        return self.sensor.luminosity

    def message_handler(self, payload):
        pass

# lightSensor = None
# keep_alive = True
#
#
# def ctrlc_handler(signum, frame):
#     global lightSensor, keep_alive
#     print("Ctrl+C received...")
#     keep_alive = False
#     lightSensor.stop()
#     lightSensor = None
#
#
# # Execution or import
# if __name__ == "__main__":
#
#     logging.basicConfig(format="[%(asctime)s][%(module)s:%(funcName)s:%(lineno)d][%(levelname)s] %(message)s",
#                         stream=sys.stdout)
#     logging.getLogger().setLevel(logging.DEBUG)
#     signal.signal(signal.SIGINT, ctrlc_handler)
#     lightSensor = LightSensor()
#
#     while keep_alive:
#         None
#
#     print("The end")
