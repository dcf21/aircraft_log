DROP USER IF EXISTS 'adsb'@'localhost';
CREATE USER 'adsb'@'localhost' IDENTIFIED BY 'beepio8D';
DROP DATABASE IF EXISTS adsb;
CREATE DATABASE adsb;
GRANT ALL ON adsb.* TO 'adsb'@'localhost';
