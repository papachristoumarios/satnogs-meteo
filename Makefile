install_dependencies:
	echo "Installing pip and dependencies from PyPI"
	apt-get install python-pip -y &&
	pip install pymongo bokeh pyserial daemon
	echo "Succesfully installed" 
	
install:
	make install_dependencies
	echo "Copying files to /opt"
	cp -a ../satnogs-meteo /opt/satnogs-meteo &&
	cd /opt/satnogs-meteo &&
	chmod +x server.py
	echo "Symlinking server.py -> /usr/bin/satnogs-meteo
	ln -s /usr/bin/satnogs-meteo /opt/satnogs-meteo/server.py
	echo "Hardlinking www/index.html to /var/www"
	ln /var/www/index.html /opt/satnogs-meteo/www/index.html
