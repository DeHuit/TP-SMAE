# Sys utils
import logging
import signal
import sys
import RPi.GPIO as GPIO
from smbus import SMBus

# Sensors
from Clock import Clock
from ShuttersController import ShuttersController
from PresemceDetector import PresenceDetector
from LampController import LampController
from TemperatureSensor import TemperatureSensor
from LuminositySensor import LuminositySensor
# import shutters


def i2c_scan():
    _I2C_ADDR_RANGE = 127
    try :
        bus = SMBus(1)
    except:
        return []
    devices = []
    for addr in range(0, _I2C_ADDR_RANGE) :
        try :
            bus.write_quick(addr, 0x00)
            devices.append(addr)
        except:
            pass
    return devices


clock = None
temperature = None
luminosity = None
shutter = None
lamp = None
presence = None
keep_alive = True

IP = "127.0.0.1"
PORT = 1883

def ctrlc_handler(signum, frame):
    global clock, temperature, luminosity, shutter, lamp, presence, keep_alive
    if clock is not None:
        clock.stop()
        clock = None
    if temperature is not None:
        temperature.stop()
        temperature = None
    if luminosity is not None:
        luminosity.stop()
        luminosity = None
    if shutter is not None:
        shutter.stop()
        shutter = None
    if lamp is not None:
        lamp.stop()
        lamp = None
    if presence is not None:
        presence.stop()
        presence = None
    keep_alive = False
    GPIO.cleanup()

def main() :
    global clock, temperature, luminosity, shutter, lamp, presence, keep_alive
    # SETTING LOGGER
    logging.basicConfig(format="[%(asctime)s][%(module)s:%(funcName)s:%(lineno)d][%(levelname)s] %(message)s",
                        stream=sys.stdout)
    logging.getLogger().setLevel(logging.DEBUG)
    # SETTING INTERRUPTER
    signal.signal(signal.SIGINT, ctrlc_handler)

    devices = i2c_scan()
    if len(devices) < 2:
        logging.getLogger().error("Not all devices are found : expected 2, got " + str(devices) + " : " + str(devices))
        return -1

    clock = Clock(ip=IP, port=PORT)
    temperature = TemperatureSensor(mqtt_ip=IP, mqtt_port=PORT)
    luminosity = LuminositySensor(mqtt_ip=IP, mqtt_port=PORT)
    shutter = ShuttersController(led_pin=19, mqtt_ip=IP, mqtt_port=PORT)
    lamp = LampController(lamp_pin=16, mqtt_ip=IP, mqtt_port=PORT)
    presence = PresenceDetector(int_pin=20, mqtt_ip=IP, mqtt_port=PORT)

    while keep_alive:
        None

    print("The end")

if __name__ == '__main__':
    main()