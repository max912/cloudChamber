### MAIN ###
import signal
import sys
import RPi.GPIO as GPIO
from WebServer import WebServer

def shutdownServer(sig, unused):
    print('Clean-up')
    GPIO.cleanup()
    server.shutdown()
    sys.exit(1)

signal.signal(signal.SIGINT, shutdownServer)
server = WebServer(8080)
server.start()
print("Press Ctrl+C to shut down server.")
