#!/usr/bin/python

import socket
import sys
import os
import signal
import RPi.GPIO as GPIO
from lib.temperature import Temperature
from lib.control import controlC, controlL, controlG
import threading
import time

socket.socket._bind = socket.socket.bind
def my_socket_bind(self, *args, **kwargs):
    self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return socket.socket._bind(self, *args, **kwargs)
socket.socket.bind = my_socket_bind

# Clean-up when press CTRL+C
def signal_handler(signal, frame):
        print('Clean-up')
        GPIO.cleanup()
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

killEvent = threading.Event()
status = {"controlsMode": 0, "pumpStatus": 0, "glassStatus": 0, "conductStatus": 0}
threads_list = []

def startThreads():
	# Daemons
	global killEvent
	killEvent = threading.Event()
	threads_list = []
	### Conduct temperature
	controlCThread = threading.Thread(target = controlC, args=(killEvent, "controlC"))
	controlCThread.setDaemon(True)
	controlCThread.start()
	threads_list.append(controlCThread)

	### Glass temperature
	controlGThread = threading.Thread(target = controlG, args=(killEvent, "controlG"))
	controlGThread.setDaemon(True)
	controlGThread.start()
	threads_list.append(controlGThread)

	### Alcohol level
	controlLThread = threading.Thread(target = controlL, args=(killEvent, "controlL"))
	controlLThread.setDaemon(True)
	controlLThread.start()
	threads_list.append(controlLThread)

def stopThreads():
	killEvent.set()
	map(threading.Thread.join, threads_list)

def getTemperature():
	#return Temperature().getTemp()
	return  ("{\"plate\": \""+str(10)+"\",\"conduct\": \""+str(5)+"\",\"glass\": \""+str(0)+"\"}")

def glassOn():
	GPIO.output(20, False)
	print("GLASS ON")
	status["glassStatus"] = 1
	return 0

def glassOff():
	GPIO.output(20, True)
	print("GLASS OFF")
	status["glassStatus"] = 0
	return 0

def pumpOn():
	GPIO.output(21, True)
	print("PUMP ON")
	status["pumpStatus"] = 1
	return 0

def pumpOff():
	GPIO.output(21, False)
	print("PUMP OFF")
	status["pumpStatus"] = 0
	return 0

def conductOn():
	GPIO.output(16, False)
	print("CONDUCT ON")
	status["conductStatus"] = 1
	return 0

def conductOff():
	GPIO.output(16, True)
	print("CONDUCT OFF")
	status["conductStatus"] = 0
	return 0

def setModeAuto():

	GPIO.cleanup()
	GPIO.setmode(GPIO.BCM)
	### Ultrasonic sensor
	GPIO.setup(23, GPIO.OUT)
	GPIO.setup(24, GPIO.IN)
	### Conduct relay
	GPIO.setup(16, GPIO.OUT)
	### Glass relay
	GPIO.setup(20, GPIO.OUT)
	### Micropump
	GPIO.setup(21, GPIO.OUT)

	glassOn()
	conductOn()
	pumpOff()

	#startThreads()
	
	status["controlsMode"] = 0
	print "Controls mode --> AUTO"
	
	return 0

def setModeMan():

	#stopThreads()
	glassOff()
	conductOff()
	pumpOff()
	
	status["controlsMode"] = 1
	print "Controls mode --> MANUAL"
	
	return 0
	
def getStatus():
	return ("{\"mode\":"+str(status["controlsMode"])+",\"pump\":"+str(status["pumpStatus"])+",\"glass\":"+str(status["glassStatus"])+",\"conduct\":"+str(status["conductStatus"])+"}")

callbacks = {"getTemperature": getTemperature, "glassOn": glassOn, "glassOff": glassOff, "pumpOn": pumpOn, "pumpOff": pumpOff, "conductOn": conductOn, "conductOff": conductOff, "setModeAuto": setModeAuto, "setModeMan": setModeMan, "getStatus": getStatus}

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('192.135.16.105', 10000)
print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)
sock.listen(1)

#setModeAuto()

while True:
	#print >>sys.stderr, 'waiting for a connection'
	connection, client_address = sock.accept()

	try:
		#print >> sys.stderr, 'connection from', client_address
		message = connection.recv(1024)
		data = callbacks[message]()

		if data != 0:
			connection.sendall(data)

	except:
		e = sys.exc_info()[0]
		print str(e)

	finally:
		connection.close()
