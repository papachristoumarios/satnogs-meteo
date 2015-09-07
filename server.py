#!/usr/bin/env python2.7
from bokeh.plotting import figure, output_server, cursession, show
from __init__ import *
import serial, json, time, pymongo, daemon, sys, os
global client
client = pymongo.MongoClient()

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
					print 'Could not open any serial port on {0}{1}. Trying with {0}{2}'.format(SERIAL_PORT_DEV,n,n+1)
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
		
		#pymongo integration
		try:
			self.db = client['meteo_db']
			self.collection = self.db.colletion['meteo_data_collection']
		except: #retry with object-style formalism
			self.db = client.meteo_db
			self.collection = self.db.collection.meteo_data_collection
			
	def update_charts(self):
		for chart in self.charts:
			chart.update()			
		
	def read_data(self):
		self.lastdata = self.ser.readline()
		return self.lastdata
		
	def parse_data(self, store_to_db=True):
		self.read_data() #read data from serial object
		self.lastjson = json.loads(self.lastdata)
		if not(len(self.lastjson) is 3):
			raise MeteoStation.ParseDataError()
		if store_to_db: # store meteo data to meteo_db.meteo_data_collection
			self.collection.insert_one(post)
		for key in self.data.keys():
			self.data[key].append(float(self.lastjson[key]))
		self.data["timenow"].append(get_time())
		self.plot_all()
		
	def plot_all(self, mode="v"):
		if not(mode is 'v' or mode is 'h'):
			raise MeteoStation.InvalidPlotArgument()
		if mode is 'v':
			vplot(*self.charts.fig)
		else:
			hplot(*self.charts.fig)
			
	def maintain(self):
		if len(self.data[self.data.keys()[0]]) > MAX_STORAGE:
			for key in self.data.keys():
				self.data[key] = []
				
	def start(self):
		while True:
			self.parse_data()
			self.update_charts()
			time.sleep(DELAY_INTERVAL)
	
	def export_data_to_file(self, outputfilename):
		if not(outputfilename.endswith('.json'):
			outputfilename += '.json'
		try:	
			os.system('mongoexport --db meteo_db --collection meteo_data_collection -o {0}'.format(outputfilename))
		except:
			raise MeteoStation.ExportError()
				
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
			
	class ExportError(Exception):
		def __init__(self):
			super(ExportError, self).__init__()

class MeteoStationDaemonizer(daemon.Daemon): #daemon wrapper for MeteoStation class
	
	def __init__(self):
		super(MeteoStationDaemonizer, self).__init__('/var/run/meteo_station.pid')
		self.meteo_station = MeteoStation()
		
	def run(self):
		self.meteo_station.start()
		
if __name__ == '__main__':
	
	assert(len(sys.argv <= 1))
	if sys.argv[0] is '--daemonized':
		meteo_station_daemon = MeteoStationDaemonizer()
		meteo_station_daemon.start()
	elif sys.argv[0] is '':
		meteo_station = MeteoStation()
		meteo_station.start()
	else:
		raise Exception('Not a valid parameter')
		sys.exit()		
	
