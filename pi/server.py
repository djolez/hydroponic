#!/usr/bin/python
from flask import Flask, request, jsonify
import db_model
from datetime import *
import serial
import serial_communication as sc
import json
import logging
import picamera
from time import sleep
import threading
import copy
import os
import camera
import requests

# TODO: cannot run this with python3, because of that needed to use IOError when reading config.json

app = Flask(__name__)
app.config.update({'DEBUG': True, 'JSONIFY_PRETTYPRINT_REGULAR': False})

db_model.init_db()

TBOT_TOKEN = 'PUT TELEGRAM BOT TOKEN HERE'


#################
#               #
#   Sensors     #
#               #
#################

@app.route('/sensors/list')
def get_sensor_list():
    res = db_model.get_all_sensor_names()

    return jsonify({'data': [e.to_dict() for e in res]})


@app.route('/sensors/stats')
def get_sensor_stats():

    available_sensors = db_model.get_all_sensor_names()
    res = []

    end = datetime.now()
    start = end - timedelta(hours=24)

    for sensor in available_sensors:
        res.append(db_model.get_sensor_stats(sensor.name, start, end))

    return jsonify({'data': res})


@app.route('/sensors/last-values')
def get_sensors_last_values():

    available_sensors = db_model.get_all_sensor_names()
    res = []

    for sensor in available_sensors:
        res.append(db_model.get_sensor_last_value(sensor.name))

    return jsonify({'data': [e.to_dict() for e in res]})

# For Notifications #
# i read that is possible to send a messages through api using post (-.-)'' -> https://api.telegram.org/bot<token>/METHOD_NAME.


def send_notif_to(user_chat_id, text):
    # send a notification to a specific user
    response = requests.post(
        url='https://api.telegram.org/bot' + TBOT_TOKEN + '/sendMessage',
        data={'chat_id': user_chat_id, 'text': str(text)}
    ).json()
    return response
# to write in the server.py


def send_notif_broadcast(text):
    # send a notification to all registered users; if something goes wrong, return false and the list of users that doesn' receive notif
    usrlist = db_model.get_all_users()
    all_sent = True
    usr_not_sent = []
    for user in usrlist:
        # print user.user_id
        response = requests.post(
            url='https://api.telegram.org/bot' + TBOT_TOKEN + '/sendMessage',
            data={'chat_id': user.user_id, 'text': str(text)}
        ).json()

        if response['ok'] is None:
            all_sent = False
            usr_not_sent.append(user)
    if all_sent:
        return True
    else:
        return (False, usr_not_sent)

# ____________ #


@app.route('/sensors/<sensor_name>')
def hello(sensor_name):

    start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d %H:%M:%S') if 'start_date' in request.args else None
    end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d %H:%M:%S') if 'end_date' in request.args else None

    res = db_model.get_sensor_data(name=sensor_name, start=start_date, end=end_date)

    return jsonify({'data': [e.to_dict() for e in res]})


def sensor_monitoring_loop(interval_in_mins):
    print('sensor_monitoring_loop: ', datetime.now())

    start = datetime.now() - timedelta(minutes=interval_in_mins)
    end = datetime.now()

    notification = db_model.Notification(entity='sensor', importance=1)

    for sensor in sensor_desired_values:
        avg = db_model.get_avg_for_sensor(sensor['name'], start, end)
        print('AVG for ' + sensor['name'] + ' = ' + str(avg))

        # there are no records
        if(avg == -1):
            continue

        notification.name = sensor['name']
        notification.value = avg
        addNotif = False

        if(avg < sensor['desiredValue']['min']):
            notification.message = 'Value too low'
            addNotif = True
        elif(avg > sensor['desiredValue']['max']):
            notification.message = 'Value too high'
            addNotif = True
        else:
            # Everything is ok, if there was a notif before make it inactive
            db_model.deactivate_last_notification('sensor', sensor['name'])

        if addNotif is True:
            notification_mes = (notification.message) + "\nin the sensor: " + str(sensor['name']) + "\nRetuned value: " + str(avg)  
            res = send_notif_broadcast(notification_mes)
            db_model.add_notification(notification)

    t = threading.Timer(interval_in_mins * 60, sensor_monitoring_loop, [interval_in_mins])
    # t = threading.Timer(sensor_check_interval, sensor_monitoring_loop, [sensor_check_interval])
    t.start()
    sensor_monitor_threads[t.name] = t


sensor_desired_values = []
sensor_check_interval = 0
sensor_monitor_threads = {}


def handle_sensors_config(config):

    if(config['sensors'] is None):
        logging.error('config.json error - missing sensors object')
    if(config['sensors']['list'] is None):
        logging.error('config.json error - missing sensors list')

    global sensor_desired_values, sensor_check_interval, sensor_monitor_threads

    sensor_desired_values = config['sensors']['list']
    sensor_check_interval = config['sensors']['checkValuesInterval']

    for key, value in copy.copy(sensor_monitor_threads).iteritems():
        sensor_monitor_threads[key].cancel()
        del sensor_monitor_threads[key]

    sensor_monitoring_loop(sensor_check_interval)

#################
#               #
#   Devices     #
#               #
#################


@app.route('/devices/<name>/<state>')
def device_change_state(name, state):

    run_time = None

    if(request.args.get('runTime')):
        run_time = int(request.args.get('runTime'))

    sc.write('device/' + name + '/' + state)
    db_model.add_device_log(db_model.Device_log(name=name, state=state))

    if run_time:
        print('HERRe ', run_time)
        next_state = 'on' if state == 'off' else 'off'

        t = threading.Timer(run_time * 60, execute_device_action, [name, None, next_state])
        t.start()

        threads[t.name] = t

    return 'OK'


@app.route('/devices')
def get_all_devices():

    res = db_model.get_all_devices()

    return jsonify({'data': [e.to_dict() for e in res]})


@app.route('/devices/actions/')
def get_device_actions_for_date():

    res = db_model.get_device_actions_for_date()

    return jsonify({'data': [e.to_dict() for e in res]})


def remove_timer_thread(name):
    del threads[name]


def execute_device_action(device_name, next_time, state):
    print('Executing action: ', device_name, state)
    sc.write('device/' + device_name + '/' + state)

    db_model.add_device_log(db_model.Device_log(name=device_name, state=state))

    remove_timer_thread(threading.current_thread().name)

    # schedule next call
    if(next_time):
        device_loop(device_name, next_time, state)

threads = {}


def device_loop(device_name, time, state):

    schedule_sec = (time - datetime.now()).total_seconds()
    print('Scheduling call: ', device_name, schedule_sec, state)

    t = threading.Timer(schedule_sec, execute_device_action, [device_name, time + timedelta(days=1), state])
    t.start()

    threads[t.name] = t

time_format_with_seconds = '%H:%M:%S'
time_format_without_seconds = '%H:%M'


def get_time_from_string(time_string):

    try:
        res = datetime.strptime(time_string, time_format_with_seconds).time()
    except ValueError:
        res = datetime.strptime(time_string, time_format_without_seconds).time()

    return res


def schedule_device(name, interval):

    if(not interval['on'] or not interval['off']):
        logging.error('config.json interval missing on/off')
        return

    on_time = get_time_from_string(interval['on'])
    off_time = get_time_from_string(interval['off'])
    now = datetime.now()

    on_datetime = datetime.combine(now, on_time)
    off_datetime = datetime.combine(now, off_time)

    # if on_time has already passed schedule for tomorrow
    if(on_datetime < now):
        on_datetime = on_datetime + timedelta(days=1)
        off_datetime = off_datetime + timedelta(days=1)

    # if off_time passed or if interval begins before and ends after now
    if(off_datetime < now or off_datetime < on_datetime):
        off_datetime = off_datetime + timedelta(days=1)

    device_loop(name, on_datetime, 'on')
    device_loop(name, off_datetime, 'off')

day_start_string = ''
day_end_string = ''


def handle_devices_config(config):

    if(config['devices'] is None):
        logging.error('config.json wrongly formatted - missing devices list')

    global threads, day_start_string, day_end_string

    for device in config['devices']:
        print('Read device: ', device['name'])

        try:
            if(device['intervals']):
                for interval in device['intervals']:
                    if(device['name'] == 'light'):
                        day_start_string = interval['on']
                        day_end_string = interval['off']

                    schedule_device(device['name'], interval)
        except KeyError:
            logging.error('config.json wrongly formatted - missing devices/intervals')


#################
#               #
#   Config      #
#               #
#################

# Default config (in case that there is no config.json file)
config = {
    'deviceSetup': {
        'daylight': 16,
        'dayStart': '08:00',
        'floods': 2
    },
    'devices': [{
        'name': 'light',
        'intervals': []
    }, {
        'name': 'water_pump',
        'intervals': []
    }],
    'sensors': {
        'updateInterval': 60,
        'checkValuesInterval': 60,
        'list': [{
            'name': 'waterTemp',
            'desiredValue': {
                'min': 18,
                'max': 26
            }
        }]
    }
}


@app.route('/config', methods=['GET'])
def get_config():

    return jsonify(**config)


@app.route('/config', methods=['PUT'])
def update_config():
    try:
        data = json.loads(request.data)

        with open('config.json', 'w') as config_file:
            json.dump(data, config_file)
            global config
            config = data
            apply_config(config)
    except IOError:
        logging.error('File config.json not found')

    return 'OK'


def apply_config(config):

    tmp = copy.copy(threads)

    for name, t in tmp.iteritems():
        t.cancel()
        remove_timer_thread(name)

    handle_devices_config(config)
    handle_sensors_config(config)


def read_config():

    try:
        with open('config.json') as config_file:
            global config
            config = json.load(config_file)
            apply_config(config)
    except IOError:
        logging.error('File config.json not found')


#####################
#                   #
#   Notifications   #
#                   #
#####################

@app.route('/notifications')
def get_all_notifications():
    res = db_model.get_all_notifications()

    return jsonify({'data': [e.to_dict() for e in res]})


#################
#               #
#   Camera      #
#               #
#################

@app.route('/camera/take-picture')
def take_picture():

    camera_config = {}
    if('width' in request.args and 'height' in request.args):
        width = int(request.args.get('width'))
        height = int(request.args.get('height'))
    else:
        width = 1920
        height = 1080

    camera_config['resolution'] = (width, height)

    res = camera.take_picture(camera_config)

    return jsonify({'name': res})


def is_daytime():
    now = datetime.now()
    now_time = now.time()

    # All of this is needed to determine if we are in the timeframe of the light specified in settings
    try:
        day_start = datetime.strptime((now.strftime('%Y-%m-%d') + ' ' + day_start_string), '%Y-%m-%d ' + time_format_with_seconds)
    except ValueError as e:
        day_start = datetime.strptime((now.strftime('%Y-%m-%d') + ' ' + day_start_string), '%Y-%m-%d ' + time_format_without_seconds)

    # day_end is after 00:00
    if(day_start_string > day_end_string):
        try:
            day_end = datetime.strptime(((now + timedelta(hours=24)).strftime('%Y-%m-%d') + ' ' +
                                         day_end_string), '%Y-%m-%d ' + time_format_with_seconds)
        except ValueError as e:
            day_end = datetime.strptime(((now + timedelta(hours=24)).strftime('%Y-%m-%d') + ' ' +
                                         day_end_string), '%Y-%m-%d ' + time_format_without_seconds)

    else:
        try:
            day_end = datetime.strptime((now.strftime('%Y-%m-%d') + ' ' + day_end_string), '%Y-%m-%d ' + time_format_with_seconds)
        except ValueError as e:
            day_end = datetime.strptime((now.strftime('%Y-%m-%d') + ' ' + day_end_string), '%Y-%m-%d ' + time_format_without_seconds)

    return (day_start <= now <= day_end)


def timelapse_photo(interval_mins):
    print('******** TAKING PICTURE ' + threading.current_thread().name)
    if is_daytime():
        camera.take_timelapse()

    threading.Timer(interval_mins * 60, timelapse_photo, [interval_mins]).start()


@app.route('/camera/open-timelapse')
def list_timelapse():
    
    start = datetime.strptime(request.args.get('start'), '%Y-%m-%d %H:%M:%S') if 'start' in request.args else (datetime.now() - timedelta(hours=3))
    end = datetime.strptime(request.args.get('end'), '%Y-%m-%d %H:%M:%S') if 'end' in request.args else datetime.now()
 
    imgs = (os.path.join('../web-app/img/timelapse', fn) for fn in os.listdir('../web-app/img/timelapse'))
    imgs = ((os.stat(path), path) for path in imgs)

    def get_key(item):
        return item[0][8]

    res = []

    for i in sorted(imgs, key=get_key):
        created = datetime.fromtimestamp(i[0][8])

        if start <= created <= end:
            res.append(os.path.basename(i[1]))
   
    return jsonify({'data': res})
 
if __name__ == '__main__':
    read_config()
    timelapse_photo(15)
    # sensor_monitoring_loop(10)
    app.run(host='0.0.0.0', use_reloader=False)
