import serial, sys, time

if __name__ == '__main__':	
	if sys.argv[0] == 'i2c':
		try:
			from wrappers import *
		except ImportError:
			print 'Unable to satisfy dependencies. Run sudo python setup.py install'
			sys.exit()
			
		bmp, dht = BMP180Wrapper(), DHT22Wrapper()
		try:
			print bmp.read_temp()
			print bmp.read_pres()
			print dht.read_temp()
			print dht.read_hum()
		except:
			print 'Please make sure you have set up the sensors correctly'
			sys.exit()
			
		print 'Test ran with success.'
		sys.exit()
		
	elif sys.argv[0] == 'arduino':
		MAX_SERIAL_PORTS = 10
		SERIAL_PORTS = ['/dev/ttyACM{0}'.format(i) for i in range(MAX_SERIAL_PORTS)] 
		SERIAL_PORTS.append('/dev/ttyAMA0')
		for sp in SERIAL_PORTS:
			try:
				ser = serial.Serial(sp, 9600)
				break
			except:
				ser = None
				
		if ser == None:
			print 'Failed to connect'
			sys.exit()
		else:
			for i in range(10):
				try:
					print ser.readline()
					ans = True
				except
					ans = False
				finally:
					time.sleep(2)
			
			if ans:
				print 'Test ran with successs'; sys.exit()
			else:
				print 'Failed to fetch data from serial. Check your connection again'; sys.exit()
