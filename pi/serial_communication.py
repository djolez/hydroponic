#!/usr/bin/python3

import serial
import json
import logging
import db_model
import monitoring_daemon
from pprint import pprint

serial_conn = None

def setup():
    global serial_conn
    serial_conn = serial.Serial('/dev/ttyACM0', 9600)
    db_model.init_db() 
    
    monitoring_daemon.start()


def get_key_name(item):
    return list(item.keys())[0]

def save_sensor_reading1(data):
    sensor_name = get_key_name(data)
    data_copy = data[sensor_name].copy()
    
    for name in data[sensor_name]:
        #if there are multiple values add sensor name in front
        if len(list(data[sensor_name].keys())) > 1:
            data_copy[sensor_name + '_' + name] = data[sensor_name][name]
            del data_copy[name]
        
    #for name in data_copy:
    #    db_mode.add_sensor_reading({'name': name, 'value': data_copy[name]})


def save_sensor_reading(sensor_name, readings):
    if len(readings)>1:
        r = dict()
        for k, v in readings.items():
            r[sensor_name + '_' + k] = v
    else:
        r = readings
    
    pprint(r)

    for k, v in r.items():
        db_model.add_sensor_reading(db_model.Sensor_reading(name=k, value=v))
        

def main():
    global serial_conn
    line = serial_conn.readline()

    while True:
        line = str(serial_conn.readline(), 'ascii')

        try:
            print(line)

            dict_obj = json.loads(line)
            if 'sensor' in dict_obj: 
                for k,v in dict_obj['sensor'].items():
                    save_sensor_reading(k, v)

        except ValueError as e:
            logging.error('*-*-*-*-*-*-*-*-*Cannot convert str to json: {}*-*-*-*-*-*-*-*-*-*'.format(line))
            logging.exception(e)
    
if __name__ == '__main__':
    setup()
    main()
