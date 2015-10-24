import os

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

class BokehServerWrapper:
	"""Python wrapper for bokeh-server"""
	
	def __init__(self, ip, bg=True, multiuser=False):
		#import sh
		#self.cmd = sh.Command('/usr/local/bin/bokeh-server')
		self.ip = ip
		self.bg = bg
		if self.bg:
			self.cmd = 'bokeh-server --ip {0} &'.format(self.ip)
		else:
			self.cmd = 'bokeh-server --ip {0}'.format(self.ip)
		
	def run(self):
		os.system(self.cmd)
		
	def __call__(self): self.run()
