import RPi.GPIO as GPIO
import time


def getDistance():

	TRIG = 23
	ECHO = 24

	GPIO.output(TRIG, False)
	time.sleep(0.1)

	GPIO.output(TRIG, True)
	time.sleep(0.00001)
	GPIO.output(TRIG, False)

	t1 = 0
	t2 = 0

	pulse_start = 0
	pulse_end = 0

	while GPIO.input(ECHO) == 0 and t1 < 100:
		pulse_start = time.time()
		t1 += 1

	if t1 < 100:
		while GPIO.input(ECHO) == 1 and t2 < 100:
			pulse_end = time.time()
			t2 += 1

	pulse_duration = pulse_end - pulse_start

	dist = pulse_duration * 0.5 * 34300

	if t1 >= 100 or t2 >= 100:
		return -1

	return dist

def getLevel():
	dist = 0
	i = 0
	n = 0
	err = 0
	while i < 50:
		if GPIO.getmode != 11:
			break
		new_dist = getDistance()
		if new_dist > 0:
			dist += new_dist
			n += 1
		else:
			err += 1
			#print("Error while reading level sensor: "+str(err))
		i += 1
	if n > 0:
		return round(dist/n, 1)

	return -1
