import json
import logging

# MQTT related imports
import paho.mqtt.client as mqtt


class MQTTConnection:
    # #############################################################################
    #
    # Global Variables
    #
    MQTT_SERVER = "vm-dyn-0-212"
    #MQTT_SERVER = "192.168.0.102"
    MQTT_PORT = 1883
    # Full MQTT_topic = MQTT_BASE + MQTT_TYPE
    MQTT_BASE_TOPIC = None
    MQTT_TYPE_TOPIC = None
    MQTT_PUB = None

    # First subscription to same topic (for tests)
    MQTT_SUB = None
    # ... then subscribe to <topic>/command to receive orders
    # MQTT_SUB = "/".join([MQTT_PUB, "command"])

    MQTT_QOS = 0  # (default) no ACK from server
    # MQTT_QOS=1 # server will ack every message

    # Server private variables
    client = None
    log = None
    stopped = False
    # What to do on message arrival?
    uID = -1
    message_handler = None
    # #############################################################################
    #
    # Functions
    #

    def __init__(self, uID, ip="127.0.0.1", port=1883, base_topic=None, to_publish=None, to_subscribe=None, message_handler=None):
        self.uID = uID
        try:
            self.log = logging.getLogger()
            # personnalisation
            self.message_handler = message_handler
            self.MQTT_BASE_TOPIC = base_topic
            if base_topic is not None and not (base_topic[0] == '/'):
                self.MQTT_BASE_TOPIC = '/' + self.MQTT_BASE_TOPIC
            if base_topic is not None and base_topic[-1] == '/':
                self.MQTT_BASE_TOPIC = self.MQTT_BASE_TOPIC[:-1]
            if to_publish is not None:
                if base_topic is not None:
                    self.MQTT_PUB = "/".join([self.MQTT_BASE_TOPIC,  to_publish])
                else:
                    self.MQTT_PUB = to_publish
            if to_subscribe is not None:
                if base_topic is not None:
                    self.MQTT_SUB = "/".join([self.MQTT_BASE_TOPIC,  to_subscribe])
                else:
                    self.MQTT_SUB = to_subscribe
            # MQTT setup
            self.MQTT_SERVER = ip
            self.MQTT_PORT = int(port)
            self.client = mqtt.Client(clean_session=True, userdata=None)
            self.client.on_connect = self.on_connect
            if message_handler is not None:
                self.client.on_message = self.on_message
            self.client.on_publish = self.on_publish
            self.client.on_subscribe = self.on_subscribe
            # Start MQTT operations
            self.client.connect(host=self.MQTT_SERVER, port=self.MQTT_PORT, keepalive=60)
            self.client.loop_start()
            self.log.info("Connection established")
        except Exception as e:
            self.log.error("Some error occurred : " + str(e))
            raise e

    def __del__(self):
        if not self.stopped:
            self.stop()

    def stop(self):
        self.stopped = True
        self.log.info("[Shutdown] stop MQTT operations ...")
        if self.MQTT_SUB is not None:
            self.client.unsubscribe(self.MQTT_SUB)
        if self.client is not None:
            self.client.disconnect()
            self.client.loop_stop()
            del self.client



    # --- MQTT related functions --------------------------------------------------
    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        self.log.info("Connected with result code : %d" % rc)
        if rc == 0:
            # Subscribe to topic
            if self.MQTT_SUB is not None:
                self.log.info("subscribing to topic: %s" % self.MQTT_SUB)
                self.client.subscribe(self.MQTT_SUB)

    # The callback for a received message from the server.
    def on_message(self, client, userdata, msg):
        payload = None
        try:
            payload = json.loads(msg.payload.decode('utf-8'))
        except Exception as e:
            self.log.error("Error extracting payload : " + str(e))
            return
        try :
            if self.message_handler is not None:
                self.message_handler(payload)
            else:
                self.log.warning("No message handler! Message is not precessed")
        except KeyError as ke:
            self.log.error("Incoming message have no 'uID' section : " + str(ke))
            return

    # The callback to tell that the message has been sent (QoS0) or has gone
    # through all of the handshake (QoS1 and 2)
    def on_publish(self, client, userdata, mid):
        self.log.debug("mid: " + str(mid) + " published!")

    def on_subscribe(self, mosq, obj, mid, granted_qos):
        self.log.debug("Subscribed: " + str(mid) + " " + str(granted_qos))

    def on_log(self, mosq, obj, level, string):
        self.log.debug(string)

    def publish(self, frame):
        if self.MQTT_PUB is not None:
            self.client.publish(self.MQTT_PUB, json.dumps(frame), self.MQTT_QOS)
        self.log.info("Data published")

    def subscribe(self, topic):
        self.client.subscribe(topic)


# def handler(payload):
#     print("Incomming msg " + str(payload))
#
#
# def ctrlc_handler(signum, frame):
#     global keep, c
#     keep = False
#     del c
#
#
# signal.signal(signal.SIGINT, ctrlc_handler)
#
# c = MQTTConnection(1, handler)
# keep = True
# while keep:
#     None
#
# print("the end")
