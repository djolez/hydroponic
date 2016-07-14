#!/usr/bin/python3

from datetime import *
import logging
import threading
import db_model
import serial_communication as sc

##### Sensors #####

def retrieve_all_sensor_data(loop_time):

    #sc.write('sensor/get/waterFlow')
    sc.write('sensor/get/DHT')
    sc.write('sensor/get/light')
    sc.write('sensor/get/waterTemp')

    if(loop_time):
        threading.Timer(loop_time, retrieve_all_sensor_data, [loop_time]).start()


updateInterval = 60

if __name__ == '__main__':
    db_model.init_db()
    retrieve_all_sensor_data(updateInterval)
    #sensor_monitoring_loop(60)


