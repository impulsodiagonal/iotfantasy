#!/usr/bin/env python
import pyxel
import random
import uuid
import json
import paho.mqtt.client as mqtt
from datetime import datetime
from config import ROOT, PROJECT, BROKER

# MQTT stuff...
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    mqtt_client.subscribe(f'{ROOT}/#')

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# TODO: use config file
mqtt_client.connect(BROKER, 1883, 60)

mqtt_client.loop_start()

class Bus:
    def __init__(self):
        self.tick = 0
        self.uuid = str(uuid.uuid4())
        self.IN = f'{ROOT}/{self.uuid}/in'
        self.OUT = f'{ROOT}/{self.uuid}/out'
        self.HELLO = f'{ROOT}/{self.uuid}/hello'
        
        #mqtt_client.subscribe(self.IN)
        mqtt_client.message_callback_add(self.IN, self.mqtt_callback)
        
        self.do_hello()

    def do_hello(self):
        # TODO: better hello
        payload = {
            'uuid': self.uuid,
            'timestamp': datetime.now().replace(microsecond=0).isoformat(),
            'uptime': self.tick
        }
        print(payload)
        mqtt_client.publish(self.HELLO, payload=json.dumps(payload))
        
    def mqtt_callback(self, broker, obj, msg):
        print("IN: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
        self.do_action()
    
    def do_action(self):
        pass

    def update(self):
        self.tick += 1
        if self.tick % 500 == 0:
            payload = {
                'uuid': self.uuid,
                'timestamp': datetime.now().replace(microsecond=0).isoformat(),
                'state': self.state,
                'uptime': self.tick
            }
            mqtt_client.publish(self.OUT, payload=json.dumps(payload))

class Light(Bus):
    def __init__(self):
        super().__init__()
        self.state = random.choice([False, True])
        self.x = random.randrange(236) + 10
        self.y = random.randrange(172) + 10
        
    def do_action(self):
        print(f'Change state of {self.uuid} -> {not self.state}')
        self.state = not self.state
        pyxel.play(0, 0, loop=False)

    def update(self):
        if pyxel.btnp(pyxel.KEY_1):
            if random.choice([False, True]):
                self.state = not self.state
                pyxel.play(0, 0, loop=False)

    def draw(self):
        # draw it on or off
        if self.state:
            pyxel.blt(self.x, self.y, 0, 0, 0, 7, 15, 0)
            pyxel.text(self.x, self.y-5, f'{self.uuid[:4]}:{self.uuid[-4:]}', 7)
        else:
            pyxel.blt(self.x, self.y, 0, 8, 0, 7, 15, 0)
        

class App:
    def __init__(self):
        self._items = [Light() for i in range(8)]

        pyxel.init(256, 192, caption="Fantasy IoT")
        pyxel.load("city_iot.pyxres")
        pyxel.run(self.update, self.draw)
        
        

    def update(self):
        # check quit
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        for i in self._items:
            i.update()
        

    def draw(self):
        pyxel.cls(0)
        for i in self._items:
            i.draw()
        pyxel.mouse(True)


App()
