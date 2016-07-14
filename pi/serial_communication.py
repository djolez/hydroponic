#!/usr/bin/python3

import serial
from time import sleep
import json
import logging
import db_model
from pprint import pprint
import threading

serial_conn = None

def setup():
    global serial_conn
    serial_conn = serial.Serial('/dev/ttyACM0', 9600)

    db_model.init_db() 
    
def get_key_name(item):
    return list(item.keys())[0]

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
        
def handle_msg(msg):
    
    try:
        dict_obj = json.loads(msg)
        object_name = list(dict_obj.keys())[0]

        if object_name == 'sensor': 
            for k,v in dict_obj[object_name].items():
                save_sensor_reading(k, v)
    
    except ValueError as e:
        logging.error('*-*-*-*-*-*-*-*-*Cannot convert str to json: {}'.format(msg))
        logging.exception(e)

def write(msg):
    serial_conn.write(bytearray(msg + '\n', encoding='utf-8'))

def main():
    global serial_conn

    while True:
        try:
            raw = serial_conn.readline()
            print('Received: ', raw)
            line = str(raw, 'utf-8')
        
            handle_msg(line)
            print('-----------------------------------------------')
        except TypeError as e:
            logging.exception(e)
        except OSError as e:
            logging.exception(e)

setup()
threading.Thread(target=main).start()

