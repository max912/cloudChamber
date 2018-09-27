### MAIN ###
import signal
import sys
import time
import RPi.GPIO as GPIO
from WebServer import WebServer

def shutdownServer(sig, unused):
    server.shutdown()
    print('Clean-up')
    GPIO.cleanup()
    time.sleep(1)
    sys.exit(1)

signal.signal(signal.SIGINT, shutdownServer)
server = WebServer(8080)
server.start()
print("Press Ctrl+C to shut down server.")
