import threading
import time

import RPi.GPIO as GPIO
from AbstractDevice import AbstractDevice

"""
    Shutters controller
    Control shutters position  in real life - lamps is on if ON if shutters are open, close if not
    Light depends on current time ('sun' is up from 8 AM to 20 PM)
    Controlling :
    {'type:'order', 'order':'status'} - publish status
    {'type:'order','order':'set_period', 'period':<period>, 'period_units':'s'/'m'} - to set status publication interval
    {'type:'order','order':'up'/'down'} - to move shutters
    Also Clock device should be present as time is taken from it's data
"""


class ShuttersController(AbstractDevice):
    # Private data
    order = "idle"
    status = "open"
    shutters_movement = None
    shutters_delay = 5
    position_from_top = 0  # 0 for open, 1 for close
    timer_start = 0
    sys_time = {}  # used to calculate "external" light
    # Pinout
    up_pin = 0
    down_pin = 0
    led_pin = 0

    def __init__(self, led_pin, up_led=-1, down_led=-1,
                 name="Shutters",
                 base_topic="/1R1/014/shutters", delay_sec=0,
                 mqtt_ip="127.0.0.1", mqtt_port="1883"):
        # Configuring device
        self.led_pin = led_pin
        self.up_pin = up_led
        self.down_pin = down_led
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(led_pin, GPIO.OUT)
        if up_led != -1:
            GPIO.setup(up_led, GPIO.OUT)
        if down_led != -1:
            GPIO.setup(down_led, GPIO.OUT)
        # Calling other operators
        super().__init__(self, name=name, units_name="celsius",
                         base_topic=base_topic, delay_sec=delay_sec,
                         mqtt_ip=mqtt_ip, mqtt_port=mqtt_port)
        self.connection.subscribe("/time/data")

    def get_address(self):
        return "Pin " + str(self.led_pin)

    def read_data(self):
        return {'status':self.status, 'order':self.order, 'position':self.position_from_top}

    def message_handler(self, payload):
        # self.log.debug("It's my order : " + new_order)
        if payload['order'] == "up" or payload['order'] == "down":
            self.move_shutters(payload['order'])
        elif payload['order'] == "stop":
            self.stop_order()
        elif payload['order'] == "status":
            self.publish_status()

    def on_message(self, payload):
        try:
            # Check if message is mine
            if payload['type'] == 'order':
                super(ShuttersController, self).on_message(payload)
            elif payload['type'] == 'data':
                self.sys_time = payload['value']
        except KeyError as ke:
            self.log.warning("Incoming message can't be parsed")


    # Custom methods

    def update_light(self):
        if self.sys_time['hour'] in range(8, 19):
            if self.status == 'open' or self.position_from_top <= 0.2:
                GPIO.output(self.led_pin, GPIO.HIGH)
            elif self.status == 'close' or self.position_from_top > 0.2:
                GPIO.output(self.led_pin, GPIO.LOW)

    def set_open(self):
        self.order = "idle"
        self.status = "open"
        self.publish_status()
        self.shutters_movement = None
        self.position_from_top = 0
        if self.up_pin != -1:
            GPIO.output(self.up_pin, GPIO.LOW)
        self.update_light()

    def set_close(self):
        self.order = "idle"
        self.status = "close"
        self.publish_status()
        self.shutters_movement = None
        self.position_from_top = 1
        if self.down_pin != -1:
            GPIO.output(self.down_pin, GPIO.LOW)
        self.update_light()

    def stop_order(self):
        if self.shutters_movement is not None:
            self.shutters_movement.cancel()
            self.shutters_movement.join()
            deltaT = int((time.time() - self.timer_start) / self.shutters_delay)
            self.timer_start = 0
            if self.order == "up":
                self.position_from_top = self.position_from_top - (1 - deltaT)
            elif self.order == "down":
                self.position_from_top = self.position_from_top + deltaT
            self.status = "between"
            self.order = "idle"
            self.log.debug("Stop shutter on " + str(self.position_from_top) + " from the top")
        if self.up_pin != -1:
            GPIO.output(self.up_pin, GPIO.LOW)
        if self.down_pin != -1:
            GPIO.output(self.down_pin, GPIO.LOW)
        self.update_light()
        self.publish_status()

    def move_shutters(self, direction):
        time_to_go_up = self.shutters_delay * self.position_from_top
        if direction == "down" and not (self.status == "close"):
            self.log.info("Moving shutters down")
            self.shutters_movement = threading.Timer(self.shutters_delay - time_to_go_up, self.set_close)
            self.timer_start = time.time()
            self.shutters_movement.start()
            self.order = "down"
            self.status = "between"
            if self.down_pin != -1:
                GPIO.output(self.down_pin, GPIO.HIGH)
        elif direction == "up" and self.status != "open":
            self.log.info("Moving shutters up")
            self.timer_start = time.time()
            self.shutters_movement = threading.Timer(time_to_go_up, self.set_open)
            self.shutters_movement.start()
            self.order = "up"
            self.status = "between"
            if self.up_pin != -1:
                GPIO.output(self.up_pin, GPIO.HIGH)

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
