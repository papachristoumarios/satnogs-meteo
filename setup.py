from setuptools import find_packages, setup

setup(name='satnogsmeteo',
      packages=find_packages(),
      version='0.1',
      author='SatNOGS team',
      author_email='dev@satnogs.org',
      url='https://github.com/papachristoumarios/satnogs-meteo',
      description='SatNOGS Meteorological Station with Bokeh and Motion',
      install_requires=['serial',
                        'numpy',
                        'bokeh',
						'tornado'
                        ],
      dependency_links=['https://github.com/adafruit/Adafruit_Python_BMP',
						'https://github.com/adafruit/Adafruit_Python_DHT'
						],
      scripts=['server.py', 'hardware_test.py'])
