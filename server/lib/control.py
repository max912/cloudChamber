#!/usr/bin/python

import RPi.GPIO as GPIO
from temperature import Temperature
from ultrasonic import getLevel
import time

GPIO.setmode(GPIO.BCM)

### Conduct relay
GPIO.setup(16, GPIO.OUT)

### Glass relay
GPIO.setup(20, GPIO.OUT)

### Micropump
GPIO.setup(21, GPIO.OUT)

def controlG(stop_event, arg):
	status = 1
	print "Glass ON"
	while not stop_event.is_set():
		temp = Temperature().getGlassT()
		if temp > 31 and status == 1:
			GPIO.output(20, True)
			status = 0
			print "Glass OFF"
		elif temp < 29 and status == 0:
			GPIO.output(20, False)
			status = 1 
			print "Glass ON"
		time.sleep(1)
	print ("Thread killed: %s" % arg)

def controlL(stop_event, arg):
	status = 0
	print "Pump OFF"
	while not stop_event.is_set():
		lvl = getLevel()
		if lvl > 7.2 and status == 1:
			GPIO.output(21, False)
			status = 0
			print "Pump OFF"
		elif lvl < 6.5 and status == 0:
			GPIO.output(21, True)
			status = 1
			print "Pump ON"
		time.sleep(5)
	print ("Thread killed: %s" % arg)
	
def controlC(stop_event, arg):
	status = 1
	print "Conduct ON"
	while not stop_event.is_set():
		temp = Temperature().getConductT()
		if temp > 51 and status == 1:
			GPIO.output(16, True)
			status = 0
			print "Conduct OFF"
		elif temp < 49 and status == 0:
			GPIO.output(16, False)
			status = 1
			print "Conduct ON"
		time.sleep(10)
	print ("Thread killed: %s" % arg)
