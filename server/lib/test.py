from ultrasonic import getLevel
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(24, GPIO.IN)
GPIO.output(23, False)
time.sleep(2)

while True:
	print(getLevel())
