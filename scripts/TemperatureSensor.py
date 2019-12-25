import logging
import signal
import sys

from AbstractDevice import AbstractDevice

# I2C
import board
import busio
import adafruit_mcp9808

"""
    Temperature sensor
    Publish perceived temperature
    Controlling :
    {'order':'status'} - publish status
    {'order':'set_period', 'period':<period>, 'period_units':'s'/'m'} - to set status publication interval
"""


class TemperatureSensor(AbstractDevice):
    # Private data
    i2c_address = 0x1F
    sensor = None

    def __init__(self, i2c_address=0x1F,
                 name="temperature_sensor",
                 base_topic="/1R1/014/temperature", delay_sec=60,
                 mqtt_ip="127.0.0.1", mqtt_port="1883"):
        # Configuring device
        self.i2c_address = i2c_address
        i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = adafruit_mcp9808.MCP9808(i2c, address=self.i2c_address)
        # Calling other operators
        super().__init__(self, name=name, units_name="celsius",
                         base_topic=base_topic, delay_sec=delay_sec,
                         mqtt_ip=mqtt_ip, mqtt_port=mqtt_port)

    def get_address(self):
        return self.i2c_address

    def read_data(self):
        return self.sensor.temperature

    def message_handler(self, payload):
        pass

# tempSensor = None
# keep_alive = True
#
#
# def ctrlc_handler(signum, frame):
#     global tempSensor, keep_alive
#     print("Ctrl+C received...")
#     keep_alive = False
#     tempSensor.stop()
#     tempSensor = None
#
#
# # Execution or import
# if __name__ == "__main__":
#
#     logging.basicConfig(format="[%(asctime)s][%(module)s:%(funcName)s:%(lineno)d][%(levelname)s] %(message)s",
#                         stream=sys.stdout)
#     logging.getLogger().setLevel(logging.DEBUG)
#     signal.signal(signal.SIGINT, ctrlc_handler)
#     tempSensor = TemperatureSensor()
#
#     while keep_alive:
#         None
#
#     print("The end")
