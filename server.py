#!/usr/bin/env python2.7
from bokeh.plotting import figure, output_server, cursession, show
import serial
import json
import time
import os
cmd = os.system

def read_arduino_data(s):
	data_stream = s.readline()
	while True:
		try:
			data_stream = json.loads(data_stream)
			keys = data_stream.keys()
			if 'pres' in keys and 'hum' in keys and 'temp' in keys:	
				for key in keys:
					data_stream[key] = float(data_stream[key]) #cast to floats
					return data_stream
		except ValueError:
			print 'Unable to recognize json'
		time.sleep(2)
		
def get_time(gmt=3):
	T = time.gmtime()
	h,m,s = (T.tm_hour + gmt) % 24, T.tm_min, T.tm_sec
	return "{0}:{1}:{2}".format(h,m,s)
	

def main():
	timedata = []
	tmpdata, humdata, presdata = [],[],[]
	SERIAL_PORT_DEV = '/dev/ttyACM'
	BAUDRATE = 9600
	n = 0
	while True:
		try:
			ser = serial.Serial(SERIAL_PORT_DEV + str(n), BAUDRATE)
			break
		except serial.serialutil.SerialException:
			print 'could not find serial port'
			n += 1
			
	
	#gather some data
	for i in range(10):
		data = read_arduino_data(ser)
		tmpdata.append(data['temp'])
		humdata.append(data['hum'])
		presdata.append(data['pres'])
		timedata.append(get_time())
		time.sleep(2)
	
	#bokeh related things
	output_server('arduino_data')
	
	p  = figure(plot_width=400, plot_height=400)
	p.line(timedata, tmpdata, name='temp_line')
	show(p)
	renderer = p.select(dict(name='temp_line'))
	ds = renderer[0].data_source

	
	
	#gather more data
	while True:
		data = read_arduino_data(ser)
		tmpdata.append(data['temp'])
		humdata.append(data['hum'])
		presdata.append(data['pres'])
		timedata.append(get_time())
		
		
		
		
		ds.data['y'] = tmpdata[len(tmpdata)-10:len(tmpdata)]
		cursession().store_objects(ds)
		time.sleep(2)
		
if __name__ == '__main__':
	main()	
