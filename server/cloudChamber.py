#!/usr/bin/python3

import sys
import os
import signal
import socket
import RPi.GPIO as GPIO
from flask import Flask, render_template
from lib.temperature import Temperature
from lib.control import controlT, controlL, controlP, controlG
import threading
import time

socket.socket._bind = socket.socket.bind
def my_socket_bind(self, *args, **kwargs):
    self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return socket.socket._bind(self, *args, **kwargs)
socket.socket.bind = my_socket_bind

# Clean-up when press CTRL+C
def signal_handler(signal, frame):
        # I want to release the port here
        print('Clean-up')
        GPIO.cleanup()
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

# Daemons

### Conduct temperature
controlTThread = threading.Thread(target = controlT)
controlTThread.setDaemon(True)
controlTThread.start()

### Glass temperature
controlGThread = threading.Thread(target = controlG)
controlGThread.setDaemon(True)
controlGThread.start()

### Plate temperature
controlPThread = threading.Thread(target = controlP)
controlPThread.setDaemon(True)
controlPThread.start()

### Alcohol level
controlLThread = threading.Thread(target = controlL)
controlLThread.setDaemon(True)
controlLThread.start()

### Web server
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/getSensors")
def getSensors():
    return Temperature().getTemp()
