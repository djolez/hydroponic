#Hydroponic

##Hardware

In this implementation Ebb and Flow system is used. This system works by temporarily flooding the grow tray with nutrient solution and then draining the solution back into the reservoir. When the scheduler turns the pump on nutrient solution is pumped into the grow tray. When the timer shuts the pump off the nutrient solution flows back into the reservoir. The water pump is set to come on several times a day, depending on the size and type of plants, temperature and humidity and the type of growing medium used.

![alt tag](http://gardenious.com/wp-content/uploads/2014/08/how-to-build-an-ebb-and-flow-hydroponic-system.png)

### Components used

* Arduino Uno
* Arduino relay
* DHT11 Temperature and humidity sensor
* DS18B20 Water temperature sensor
* Photocell light sensor
* Raspberry Pi 3
* Pi camera v2.1

### Useful links

System build: http://bit.ly/2alQpj7

Tips for growing in hydroponics: http://bit.ly/2a5jRJd

Pictures of system development: http://imgur.com/a/kVj2a


## Software

Raspberry Pi works as a server that collects sensor data from Arduino over USB serial communication and keeps it in a SQLite database. It is equipped with Pi camera, used for visual inspection of plants progress and capturing timelapse photos. Backend is written in Python, running Flask and using NGINX as a web server.

Web app is used for displaying the sensor data in the form of charts and working time for devices (light and water pump), providing user with configuration page where he can set on/off intervals of the devices and desired values of the sensors (used for notifying when they are out of range). From here user can take pictures manually or open the timelapse view for specified date range. Frontend is done in Angular.

![alt tag](http://i.imgur.com/KRuebK3.png)
![alt tag](http://i.imgur.com/HaghVIf.png)


Telegram bot can retrieve the data about sensor values in the last 24h, send notifications about values out of range for sensors (specified in the config part of web app) and capture pictures.

###Useful links:

Running Telegram bot in Python: http://bit.ly/2af284B

### System walkaround
https://www.youtube.com/watch?v=Uy2Df0rXX6M

### Telegram bot demo
https://www.youtube.com/watch?v=GUoj2lxdjzk

## Setting up

git clone https://github.com/djolez/hydroponic.git

Web app: Run bower install in web-app folder

Telegram bot: Add Hydrobot on Telegram

## Future upgrades

* Build case for Arduino and sensors, make light holder with adjustable height, make holder for Raspberry and camera
* Enclose the system in a box so the environment conditions can be kept at the desired values more easily
* Add wifi/ethernet shield to Arduino in order to use MQTT protocol thus removing the need for serial communication with Raspberry
* (Optimistic) Fully automated nutrient and pH regulation using pH and electrical conductivity sensors in combination with peristaltic pumps
* (Optimistic) Fully automated drain/refill of the nutrient solution

## Additional info

This project was developed for the course of "Pervasive Systems 2016", held by Prof. Ioannis Chatzigiannakis within the Master of Science in Computer Science of University of Rome "La Sapienza".

Homepage of Pervasive Systems 2016 course : http://ichatz.me/index.php/Site/PervasiveSystems2016

Homepage of Prof. Ioannis Chatzigiannakis: http://ichatz.me/index.php

Homepage of MSECS "La Sapienza": http://cclii.dis.uniroma1.it/?q=msecs
