#!/usr/bin/python3

import sys
import socket
from bokeh.plotting import figure, curdoc
from bokeh.driving import linear

p = figure(plot_width=400, plot_height=400)
q = figure(plot_width=400, plot_height=400)
r1 = p.line([], [], color = "firebrick", line_width = 2)
r2 = q.line([], [], color = "navy", line_width = 2)

r = figure(plot_width=400, plot_height=400)
r3 = r.line([], [], color = "firebrick", line_width = 2)

ds1 = r1.data_source
ds2 = r2.data_source
ds3 = r3.data_source

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('192.135.16.105', 10000)

@linear()
def updateT(step):

	sock.connect(server_address)

	try:

	    data = sock.recv(16)
	    print >>sys.stderr, 'received "%s"' % data

	finally:
		print >>sys.stderr, 'closing socket'
		sock.close()

	ds1.data['x'].append(step)
	ds1.data['y'].append(data)
	ds1.trigger('data', ds1.data, ds1.data)

	ds2.data['x'].append(step)
	ds2.data['y'].append(data)
	ds2.trigger('data', ds2.data, ds2.data)	

	ds3.data['x'].append(step)
	ds3.data['y'].append(data)
	ds3.trigger('data', ds3.data, ds3.data)

curdoc().add_root(p)
curdoc().add_root(q)
curdoc().add_root(r)

curdoc().add_periodic_callback(updateT, 3000)
