import RPi.GPIO as GPIO

from AbstractDevice import *


"""
    Lamp Controller
    Switch on/off pin that should be attached to a lamp
    Controlling :
    {'type':'order, 'order':'switch', 'value': 'on'/'off'} - to switch on/off
    {'type':'order, 'order':'set_period', 'period':<period>, 'period_units':'s'/'m'} - to set status publication interval
    {'type':'order, 'order':'status'} - publish status
"""

class LampController(AbstractDevice):
    pin = 0

    def __init__(self, lamp_pin=20,
                 name="lamp",
                 base_topic="/1R1/014/lamp/", delay_sec=60,
                 mqtt_ip="127.0.0.1", mqtt_port="1883"):
        self.pin = lamp_pin
        # Setting up GPIO
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(GPIO.LOW)
        # Setting interruptions
        super().__init__(name=name, units_name="bool",
                        base_topic=base_topic, delay_sec=delay_sec,
                        mqtt_ip=mqtt_ip, mqtt_port=mqtt_port)

    def get_address(self):
        return "Pin " + str(self.pin)

    def message_handler(self, payload):
        try :
            if payload['order'] == 'switch':
                GPIO.output(GPIO.HIGH if payload['value'] else GPIO.LOW)

        except KeyError:
            self.log.warning("Unknown order")

    def read_data(self):
        return GPIO.input(self.pin)
