import socket
import sys
import os
import signal
import RPi.GPIO as GPIO
from lib.temperature import Temperature
from lib.control import controlC, controlL, controlG
import threading
import time
import datetime
import random
import subprocess

GPIO.setwarnings(False)

### GPIO SETUP
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
### High Voltage
GPIO.setup(26, GPIO.OUT)


killEvent = threading.Event()
status = {"controlsMode": 0, "pumpStatus": 0, "glassStatus": 0, "conductStatus": 0, "hvStatus": 0}
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
	return Temperature().getTemp()
        ##### DEBUG
	#date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	#return  ("{\"plate\": \""+str(random.randint(1,50))+"\",\"conduct\": \""+str(random.randint(1,50))+"\",\"glass\": \""+str(random.randint(1,50))+"\", \"date\":\""+str(date)+"\"}")

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

def hvOn():
	GPIO.output(26, True)
	print("HV ON")
	status["hvStatus"] = 1
	return 0

def hvOff():
	GPIO.output(26, False)
	print("HV OFF")
	status["hvStatus"] = 0
	return 0

def setModeAuto():

	glassOff()
	conductOff()
	pumpOff()
	
	startThreads()
	
	status["controlsMode"] = 0
	print "Controls mode --> AUTO"
	
	return 0

def setModeMan():

	stopThreads()
	glassOff()
	conductOff()
	pumpOff()
	
	status["controlsMode"] = 1
	print "Controls mode --> MANUAL"
	
	return 0
	
def getStatus():
	return ("{\"mode\":"+str(status["controlsMode"])+",\"pump\":"+str(status["pumpStatus"])+",\"glass\":"+str(status["glassStatus"])+",\"conduct\":"+str(status["conductStatus"])+",\"hv\":"+str(status["hvStatus"])+"}")


def videoRec(par):
	t = par.split("&")[0].split("=")[1]
	n = par.split("&")[1].split("=")[1]
	return subprocess.call(["./videoRec.sh", t, n])

def videoPrev(par):
	t = par.split("=")[1]
	return subprocess.call(["./videoPrev.sh", t])

callbacks = {"getTemperature": getTemperature, "glassOn": glassOn, "glassOff": glassOff, "pumpOn": pumpOn, "pumpOff": pumpOff, "conductOn": conductOn, "conductOff": conductOff, "setModeAuto": setModeAuto, "setModeMan": setModeMan, "getStatus": getStatus, "hvOn": hvOn, "hvOff": hvOff, "videoRec": videoRec, "videoPrev": videoPrev}




def bootstrap():
	time.sleep(3)
	print("Starting the cloud chamber monitoring system...")
	glassOff()
	pumpOff()
	conductOff()
	hvOff()
	while Temperature().getPlateT() > -8:
		print("Waiting for plate to reach -8 C... current temperature is "+str(Temperature().getPlateT()))
		time.sleep(10)
	setModeAuto()


bootstrapThread = threading.Thread(target = bootstrap)
bootstrapThread.setDaemon(True)
bootstrapThread.start()


class WebServer(object):

    def __init__(self, port=10000):
        self.host = "192.135.16.105" #socket.gethostname().split('.')[0] # Default to any available network interface
        self.port = port
        self.content_dir = '/home/pi/cloudChamber/server/web' # Directory where webpage files are stored
        self.server_address = ('192.135.16.105', port)

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            print("Starting server on {host}:{port}".format(host=self.host, port=self.port))
            self.socket.bind((self.host, self.port))
            print("Server started on port {port}.".format(port=self.port))

        except Exception as e:
            print("Error: Could not bind to port {port}".format(port=self.port))
            self.shutdown()
            sys.exit(1)

        self._listen() # Start listening for connections

    def shutdown(self):
        try:
            print("Shutting down server")
            stopThreads()
            s.socket.shutdown(socket.SHUT_RDWR)
            time.sleep(2)

        except Exception as e:
            pass # Pass if socket is already closed

    def _generate_headers(self, response_code):

        header = ''
        if response_code == 200:
            header += 'HTTP/1.1 200 OK\n'
        elif response_code == 404:
            header += 'HTTP/1.1 404 Not Found\n'

        time_now = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
        header += 'Date: {now}\n'.format(now=time_now)
        header += 'Server: Simple-Python-Server\n'
        header += 'Connection: close\n\n' # Signal that connection will be closed after completing the request
        return header

    def _listen(self):
        self.socket.listen(5)
        while True:
            (client, address) = self.socket.accept()
            client.settimeout(60)
#            print("Recieved connection from {addr}".format(addr=address))
            threading.Thread(target=self._handle_client, args=(client, address)).start()

    def _handle_client(self, client, address):
        PACKET_SIZE = 1024
        while True:
#            print("CLIENT",client)
            data = client.recv(PACKET_SIZE).decode() # Recieve data packet from client and decode
            
            if not data: break
			
            request_method = data.split(' ')[0]
#            print("Method: {m}".format(m=request_method))
#            print("Request Body: {b}".format(b=data))

            if request_method == "GET" or request_method == "HEAD":
                # Ex) "GET /index.html" split on space
                file_requested_par = data.split(' ')[1]

                # If get has parameters ('?'), ignore them
                file_requested =  file_requested_par.split('?')[0]
                par = None

                if len(file_requested_par.split('?')) == 2:
	                par = file_requested_par.split('?')[1]

                if file_requested == "/":
                    file_requested = "/index.html"
                
                request = file_requested.split('/')[1]

                if request in callbacks:
                    response_header = self._generate_headers(200)

                    if par:
                    	response_data = str(callbacks[request](par))
                    else:
                    	response_data = str(callbacks[request]())
                
                else:
                    filepath_to_serve = self.content_dir + file_requested
#                    print("Serving web page [{fp}]".format(fp=filepath_to_serve))

                    # Load and Serve files content
                    try:
                        f = open(filepath_to_serve, 'rb')
                        if request_method == "GET": # Read only for GET
                            response_data = f.read()
                        f.close()
                        response_header = self._generate_headers(200)

                    except Exception as e:
#                        print("File not found. Serving 404 page.")
                        response_header = self._generate_headers(404)

                        if request_method == "GET": # Temporary 404 Response Page
                            response_data = "<html><body><center><h1>Error 404: File not found</h1></center><p>Head back to <a href="/">dry land</a>.</p></body></html>"


                response = response_header.encode()
                if request_method == "GET":
                    response += response_data

                client.sendall(response)
                client.close()
                break
            else:
                print("Unknown HTTP request method: {method}".format(method=request_method))
