# Complete project details at https://RandomNerdTutorials.com

import time
import ubinascii
import machine
import micropython
import network
import esp

from umqttsimple import MQTTClient
from config import SSID, PASSWORD, MQTT_SERVER

esp.osdebug(None)
import gc
gc.collect()


client_id = ubinascii.hexlify(machine.unique_id())
topic_sub = b'notification'
topic_pub = b'hello'

last_message = 0
message_interval = 5
counter = 0

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(SSID, PASSWORD)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())

