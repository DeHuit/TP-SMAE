import RPi.GPIO as GPIO

from AbstractDevice import *

"""
    Presence Detector
    Detect interrupt received from the button to tell simulate presence of someone in the room
    Controlling :
    Controlling as any device : 
    {'type':'order','order':'status'} - publish status
    {'type':'order','order':'set_period', 'period':<period>, 'period_units':'s'/'m'} - to set status publication interval
"""


class PresenceDetector(AbstractDevice):
    pin = 0
    present = False

    def __init__(self, int_pin=20,
                 name="presence_detector",
                 base_topic="/presence_detector/", delay_sec=60,
                 mqtt_ip="127.0.0.1", mqtt_port="1883"):
        self.pin = int_pin
        # Setting up GPIO
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        # Setting interruptions
        GPIO.add_event_detect(self.pin, GPIO.RISING, callback=self.interrupt_callback, bouncetime=100)
        super().__init__(name=name, units_name="bool",
                         base_topic=base_topic, delay_sec=delay_sec,
                         mqtt_ip=mqtt_ip, mqtt_port=mqtt_port)

    def interrupt_callback(self, channel):
        self.present = not self.present
        self.publish_status()

    def get_address(self):
        return "Pin " + str(self.pin)

    def message_handler(self, payload):
        return  # No additional callback needed, it's just a sensor

    def read_data(self):
        return self.present
