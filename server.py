#!/usr/bin/env python2.7
from bokeh.plotting import figure, output_server, cursession, show, vplot, hplot
from bokeh.session import Session
from __init__ import *
import json, time, pymongo, daemon, sys, os, socket
global client, output_server, uptime_start
if os.name != "nt":
    import fcntl
    import struct

    def get_interface_ip(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s',
                                ifname[:15]))[20:24])
def get_lan_ip():
    ip = socket.gethostbyname(socket.gethostname())
    if ip.startswith("127.") and os.name != "nt":
        interfaces = [
            "eth0",
            "wlan0",
            "wlan1"
            ]
        for ifname in interfaces:
            try:
                ip = get_interface_ip(ifname)
                break
            except IOError:
                pass
    return ip


client = pymongo.MongoClient()
output_server = output_server('meteo_data', url='http://{0}:{1}'.format(get_lan_ip(), 5006))
uptime_start = time.time()

#return time as HH:MM:SS
def get_time(gmt=3):
	T = time.gmtime()
	h,m,s = (T.tm_hour + gmt) % 24, T.tm_min, T.tm_sec
	return "{0}:{1}:{2}".format(h,m,s)

class DHT22Wrapper:
	"""Wrapper for DHT22 Sensor"""
	
	def __init__(self, pin = 4):
		import Adafruit_DHT
		self.sensor = Adafruit_DHT.DHT22
		self.pin = pin
		
	def read_data(self):
		return Adafruit_DHT.read_retry(self.sensor, self.pin)
		
	def read_hum(self):
		return float(self.read_data()[0])
		
	def read_temp(self):
		return float(self.read_data()[1])
		
class BMP180Wrapper:
	"""Wrapper for BMP180 Sensor"""
	
	def __init__(self):
		import Adafruit_BMP.BMP085 as BMP
		self.sensor = BMP.BMP085()
		
	def read_temp(self):
		return float(self.sensor.read_temperature())
		
	def read_pres(self):
		return float(self.sensor.read_pressure())	


class MeteoStation:
	
	@property
	def mode(self):
		return self._mode
		
	@mode.setter
	def mode(self,value):
		if self.modeset:
			raise Exception('Mode already set to {0}'.format(self._mode))
		else:
			self._mode = value
		
	@mode.getter
	def mode(self):
		return self._mode
	
	def __init__(self, mode = 'arduino',serialObject=None): #nof indicates number of json fields
		self.mode = mode
		self.modeset = True
		if mode is 'arduino':
			import serial
			if serialObject is None:
				n=0
				while True:
					try:
						self.ser = serial.Serial(SERIAL_PORT_DEV + str(n), BAUDRATE)
						break
					except serial.serialutil.SerialException:
						print 'Could not open any serial port on {0}{1}. Trying with {0}{2}'.format(SERIAL_PORT_DEV,n,n+1)
						n += 1
			else:
				self.ser = serialObject
				self.ser.open()
		elif mode is 'rpi':
			self.bmp, self.dht = BMP180Wrapper(), DHT22Wrapper() 
			
		self.data = {}
		self.data["temp"], self.data["hum"], self.data["pres"], self.data["timenow"] = [],[],[],[]
		self.lastdata = ''; self.lastjson = None
		
		#charts
		self.tempchart, self.preschart, self.humchart = MeteoStation.MeteoChart('temp', 'Temperature', 'Temperature in *C'), MeteoStation.MeteoChart('pres','Pressure', 'Pressure in hPa'), MeteoStation.MeteoChart('hum','Humidity', 'Humidity in %RH')
		self.charts = [self.tempchart, self.preschart, self.humchart]
		self.figs = [chart.fig for chart in self.charts]
		self.show_all()
		cursession().publish()
	
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
		if self.mode is 'arduino':
			try:
				self.lastdata = self.ser.readline()
				return self.lastdata
			except:
				return
		elif self.mode is 'rpi':
			try:
				self.lastdata = json.dumps({'temp': str((self.dht.read_temp()+self.bmp.read_temp())/2), 'hum': str(self.dht.read_hum()), 'pres': str(self.bmp.read_pres())})
				print self.lastdata
				return self.lastdata
			except:
				return
			
	def parse_data(self, store_to_db=True):
		self.read_data() #read data from serial object
		try:
			self.lastjson = json.loads(self.lastdata)
		except:
			return
		if not(len(self.lastjson) is 3):
			print 'Data could not be parsed'; return
		if store_to_db: # store meteo data to meteo_db.meteo_data_collection
			self.collection.insert_one(self.lastjson)
		for key in self.data.keys():
			if key is not 'timenow':
				self.data[key].append(float(self.lastjson[key]))
			print '{0}:{1}'.format(key, self.data[key][-1:])
		self.data["timenow"].append(get_time())		
		for chart in self.charts: #append to charts datasource
			chart.append_meteo_data(self.data)
		#print 'Appended meteo data successfuly to charts'
		
	def get_plot(self, mode="v"):
		if not(mode is 'v' or mode is 'h'):
			raise MeteoStation.InvalidPlotArgument()
		if mode is 'v':
			return vplot(*self.figs)
		else:
			return hplot(*self.figs)
			
	def show_all(self):
		show(self.get_plot()); 
			
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
		if not(outputfilename.endswith('.json')):
			outputfilename += '.json'
		try:	
			os.system('mongoexport --db meteo_db --collection meteo_data_collection -o {0}'.format(outputfilename))
		except:
			raise MeteoStation.ExportError()
				
	class MeteoChart:
		"""Meteo Chart class"""
		
		def __init__(self, name, title='', y_label='', plot_width=400, plot_height=400):
			#self.fig = figure(plot_width, plot_height, name)
			self.name = name
			if title is '':
				title = name
			self.fig = figure(title=title, x_axis_label='Uptime in sec', y_axis_label = y_label)
			self.fig.line([],[], name=self.name)
			self.renderer = self.fig.select(dict(name=self.name))
			self.data_source = self.renderer[0].data_source
			
		def append_datum(self,x,y):
			self.data_source.data['x'].append(x)
			self.data_source.data['y'].append(y)
		
		def append_meteo_data(self, d):
			self.data_source.data['x'].append(time.time()-uptime_start)
			self.data_source.data['y'].append(d[self.name][-1])
			#self.update()
									
		def update(self):
			cursession().store_objects(self.data_source)
			#print 'Stored data to current session'
				
		def show(self):
			show(self.fig)
			
		def change_mode(self):
			if self.mode is 'rpi': self.mode = 'arduino'
			if self.mode is 'arduino': self.mode = 'rpi'
			
		class InvalidChartData(Exception):
			def __init__(self):
				super(InvalidChartData, self).__init__()

	class ParseDataError(Exception):
		def __init__(self):
			super(ParseDataError, self).__init__()
	
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
	
	assert(len(sys.argv) <= 1)
	if sys.argv[0] is '--daemonized':
		meteo_station_daemon = MeteoStationDaemonizer()
		meteo_station_daemon.start()
	else:
		meteo_station = MeteoStation(mode='rpi')
		meteo_station.start()
	#else:
	#	raise Exception('Not a valid parameter')
	#	sys.exit()		
