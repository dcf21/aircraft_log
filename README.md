# Aircraft ADS-B database

This is a quick-and-dirty database and web interface I built for storing an archive of the historical positions of aircraft, as detected using a USB Flight Aware Pro Stick, which is cheaply available to buy online. It receives the GPS positions as reported by aircraft via ADS-B, on a radio frequency of 1090 MHz.

Flight Aware have made available open-source [software](https://uk.flightaware.com/adsb/piaware/) for decoding the data stream from the USB Flight Aware Pro Stick. The code in this repository builds on that software, providing a database for storing positions, and a web interface for browsing them.

The build instructions below assume that you are building the software on a Raspberry Pi with a clean installation of Raspberry Pi OS. However, they will work essentially unchanged on any Ubuntu or Debian system.

## Installation commands

```
# Install required packages
apt-get update ; apt-get dist-upgrade
apt-get install screen openssh-server git vim nodejs npm pyxplot
apt-get -y install gpsd gpsd-clients libjpeg8-dev libpng-dev libgsl-dev git qiv mplayer libv4l-dev libavutil-dev libavcodec-dev libavformat-dev libx264-dev scons libcairo2-dev libcfitsio-dev libnetpbm10-dev netpbm python3-dev python3-astropy python3-numpy python3-scipy python3-pil python3-dateutil python3-pip swig ffmpeg python3-setuptools python3-virtualenv apache2 libapache2-mod-wsgi-py3 python3-tornado python3-flask build-essential libpcre++-dev libboost-dev libboost-program-options-dev libboost-thread-dev libboost-filesystem-dev libblas-dev liblapack-dev gfortran libffi-dev libssl-dev imagemagick gphoto2 libbz2-dev php-db php-mysql php-pear libapache2-mod-php mariadb-server mariadb-client libmariadbclient-dev software-properties-common cmake astrometry.net astrometry-data-tycho2 python-virtualenv python-pip python-dev libxml2-dev libxslt-dev certbot

# Enable sshd
raspi-config 

# Install the Flight Aware software for decoding data from a USB Flight Aware Pro ADS-B receiver
wget https://uk.flightaware.com/adsb/piaware/files/packages/pool/piaware/p/piaware-support/piaware-repository_5.0_all.deb
dpkg -i piaware-repository_5.0_all.deb
apt-get update
apt-get install dump1090-fa
sudo rmmod dvb_usb_rtl28xxu

# Install nodejs modules we use to build the database web interface
npm install -g bower uglify-js less less-plugin-clean-css

# Flight Aware software enables its own web interface which conflicts with Apache's use of port 80; move it to port 8080
vim /etc/lighttpd/lighttpd.conf   # Change server.port to 8088
sudo /etc/init.d/lighttpd restart

# Configure Apache to host our custom web interface. Create a quick-and-dirty self-signed https certificate
cd /etc/apache2
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout web_interface_cert.key -out web_interface_cert.pem -subj '/CN=localhost'
cd /etc/apache2/sites-available

# Map the virtual host adsb.local to /home/pi/adsb/auto/html. This directory is created when we run ./DoAll below.
vim adsb.local.conf
cd /etc/apache2/sites-enabled
ln -s ../sites-available/adsb.local.conf

# Enable useful Apache modules...
cd /etc/apache2/mods-enabled
ln -s ../mods-available/headers.load
ln -s ../mods-available/rewrite.load
ln -s ../mods-available/ssl.conf
ln -s ../mods-available/ssl.load
ln -s ../mods-available/socache_shmcb.load
service apache2 restart

# Create MySQL database and users we will use
cat build/initdb/dbinfo/db_setup.sql | sudo mysql -u root

# Create the database schema we will use, and build the web interface
./DoAll

# Start listening for ADS-B traffic
timedatectl set-timezone UTC
service dump1090-fa restart
cd /home/pi/ads_b/build/receiver
./receiver.py
```

## Accessing the web interface

The Raspberry Pi should now be hosting a web interface on the virtual host <adsb.local>.

