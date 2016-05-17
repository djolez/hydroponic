#!/usr/bin/python3

import datetime
import threading
import db_model

def check_temp():
    pass
    """
    res = db_model.get_sensor_data('temp', 120)
    print('RESULT: ', res)
    for i, item in enumerate(res):
        print(item.name, item.value, item.timestamp)

    #threading.Timer
    """
def start():
    check_temp()
