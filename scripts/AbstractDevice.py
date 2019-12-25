# #############################################################################
#
# Import zone
#
import threading
import logging
import random

import connection as con
from abc import ABC, abstractmethod


class AbstractDevice(ABC):
    # Device customisation
    uID = 0
    name = ""
    units_name = None
    delay = 20

    # Private data
    connection = None
    timer = None
    stopped = False

    def __init__(self, uID=-1, name="test_device", units_name="",
                 base_topic="/test_device/", delay_sec=60,
                 mqtt_ip="127.0.0.1", mqtt_port="1883"):
        if uID == -1:
            self.uID = random.randint(0, 255)
        self.units_name = units_name
        self.log = logging.getLogger()
        self.name = name
        self.delay = delay_sec
        self.connection = con.MQTTConnection(uID=self.uID,
                                             ip=mqtt_ip,
                                             port=mqtt_port,
                                             base_topic=base_topic,
                                             to_subscribe="orders",
                                             message_handler=self.on_message,
                                             to_publish="data")
        self.set_delay(self.delay)
        self.log.info(str(name) + " sensor is created")

    def __del__(self):
        if not self.stopped:
            self.stop()

    def stop(self):
        self.stopped = True
        if self.connection is not None:
            self.connection.stop()
        if self.timer is not None:
            self.timer.cancel()
            self.timer.join()
            del self.timer
        self.log.debug(str(self.name) + " sensor is deleted")

    ############ FUNCTIONS TO IMPLEMENT ###############

    @abstractmethod
    def get_address(self):
        return None

    @abstractmethod
    def message_handler(self, payload):
        pass

    @abstractmethod
    def read_data(self):
        return None

    ############ END FUNCTIONS TO IMPLEMENT ###############

    def publish_status(self):
        # generate json payload
        jsonFrame = {}
        jsonFrame['type'] = "data"
        jsonFrame['unitID'] = str(self.uID)
        jsonFrame['subId'] = str(self.get_address())
        jsonFrame['value'] = str(self.read_data())
        jsonFrame['value_units'] = self.units_name
        # ... and publish it!
        self.connection.publish(jsonFrame)
        msg = "Status published : data = " + jsonFrame['value']
        self.log.debug(msg)

    def on_message(self, payload):
        try:
            dest = payload['uID']
            # Check if message is mine
            if dest == str(self.uID) or dest == "all":
                self.log.debug("It's my order : " + str(payload))
                # Is it common order ?
                if payload['order'] == "status":  # Ask to publish
                    self.publish_status()
                elif payload['order'] == 'set_period':  # Ask to change period
                    period = int(payload['period'])
                    if payload['period_units'] == "s":
                        self.set_delay(period)
                    elif payload['period_units'] == "m":
                        self.set_delay(period * 60)
                    elif payload['period_units'] == "h":
                        self.set_delay(period * 60 * 60)
                    else:
                        self.log.warning("Unknown period units : " + str(payload['period_units']))
                else:  # No, it is something specific to an agent
                    self.message_handler(payload)
        except KeyError as ke:
            self.log.warning("Incoming message can't be parsed :"  + str(ke))

    def set_delay(self, delay=60):
        self.delay = delay
        if self.timer is not None:
            self.timer.cancel()
            self.timer.join()
        if self.delay > 0:
            self.__timer_function()

    def __timer_function(self):
        self.publish_status()
        self.timer = threading.Timer(self.delay, self.__timer_function, [])
        self.timer.start()
