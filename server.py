#!/usr/bin/env python2.7
from bokeh.plotting import figure, output_server, cursession, show
import serial
import json
import time
import os
cmd = os.system

global SERIAL_PORT_DEV; global BAUDRATE; global DELAY_INTERVAL
SERIAL_PORT_DEV, BAUDRATE, DELAY_INTERVAL = '/dev/ttyACM', 9600, 2

#return time as HH:MM:SS
def get_time(gmt=3):
	T = time.gmtime()
	h,m,s = (T.tm_hour + gmt) % 24, T.tm_min, T.tm_sec
	return "{0}:{1}:{2}".format(h,m,s)
	
class MeteoStation:
	
	def __init__(self, serialObject=None): #nof indicates number of json fields
		if serialObject is None:
			def _generate_serial_object():
				n=0
				while True:
				try:
					ser = serial.Serial(SERIAL_PORT_DEV + str(n), BAUDRATE)
					break
				except serial.serialutil.SerialException:
					print 'could not find serial port'
					n += 1
				return ser
			self.ser = _generate_serial_object()
		else:
			self.ser = serialObject
		self.data = {}
		self.data["temp"], self.data["hum"], self.data["pres"], self.data["timenow"] = [],[],[],[]
		self.lastdata = ''; self.lastjson = None
		self.output_server = output_server('arduino_data')
		
		#charts
		self.tempchart, self.preschart, self.humchart = MeteoStation.MeteoChart('temp'), MeteoStation.MeteoChart('pres'), MeteoStation.MeteoChart('hum')
		self.charts = [self.tempchart, self.preschart, self.humchart]
		
	def update_charts(self):
		for chart in self.charts:
			chart.update()			
		
	def read_data(self):
		self.lastdata = self.ser.readline()
		return self.lastdata
		
	def parse_data(self):
		self.read_data() #read data from serial object
		self.lastjson = json.loads(self.lastdata)
		if not(len(self.lastjson) is 3):
			raise MeteoStation.ParseDataError()
		
		for key in self.data.keys():
			self.data[key].append(float(self.lastjson[key]))
		self.data["timenow"].append(get_time())
		
	def plot_all(self, mode="v"):
		if not(mode is 'v' or mode is 'h'):
			raise MeteoStation.InvalidPlotArgument()
			
		if mode is 'v':
			vplot(*self.charts.fig)
		else:
			hplot(*self.charts.fig)
		
				
	class MeteoChart:
		
		def __init__(self, name, plot_width=400, plot_height=400):
			self.fig = figure(plot_width, plot_height, name)
			self.fig.line([],[], dict(name))
			self.name = name
			self.renderer = self.fig.select(dict(name))
			self.data_source = self.renderer[0].data_source
			
		def append_datum(self,x,y):
			self.data_source['x'].append(x)
			self.data_source['y'].append(y)
		
		def append_meteo_data(self, d):
			self.data_source['x'].append(d['timenow'][len(d['timenow'])
			self.data_source['y'].append(d[self.name][len(d[self.name])
						
		def update(self):
			cursession().store_objects(self.data_source)
				
		def show(self):
			show(self.fig)
			
		class InvalidChartData(Exception):
			def __init__(self):
				super(InvalidChartData, self).__init__()

	class ParseDataError(ParseError):
		def __init__(self):
			super(MeteoStationException, self).__init__()
	
	class InvalidPlotArgument(Exception):
		def __init__(self):
			super(InvalidPlotArgument, self).__init__()
