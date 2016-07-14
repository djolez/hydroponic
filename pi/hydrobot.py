# import sys
import requests
import datetime
import telepot
import db_model as dm
from peewee import *
import time
import urllib2
import json
from requests.auth import HTTPBasicAuth
# from pprint import pprint

"""
A simple bot that accepts two commands:
- /roll : reply with a random integer between 1 and 6, like rolling a dice.
- /time : reply with the current time, like a clock.
INSERT TOKEN below in the code, and run:
$ python name_bot.py
Ctrl-C to kill.
"""

#____Params_____ #
_USER = "djolez"
_PASS = "djole334"
PIC_DIR = '../web-app/img/'


db_proxy = Proxy()


class BaseModel(Model):

    class Meta:
        database = db_proxy


class Users(BaseModel):
    user_id = CharField()

    class Meta:
        database = db_proxy

    def __str__(self):
        return 'ID: {}'.format(self.user_id)

    def to_dict(self):
        return self.__dict__['_data']


def init_db(file_path='db/db.sqlite'):
    db_proxy.initialize(SqliteDatabase(file_path))
    db_proxy.create_tables([Users], safe=True)


def add_id(u_id):
    db_proxy.connect()
    # res = user_id.save()
    u_id.save()
    db_proxy.close()

TBOT_TOKEN = 'PUT TELEGRAM BOT TOKEN HERE'

bot = telepot.Bot(TBOT_TOKEN)
init_db()
dm.init_db()

# i read that is possible to send a messages through api using post (-.-)'' -> https://api.telegram.org/bot<token>/METHOD_NAME.
# def send_notif_to(user_chat_id):
#     # send a notification to a specific user
#     bot.sendMessage(user_chat_id, str(datetime.datetime.now()))

# to write in the server.py
# def send_notif_broadcast():
#     # send a notification to all registered users
#     usr = Users.select(Users.user_id)
#     for user in usr:
#         print user.user_id
#         bot.sendMessage(user.user_id, str(datetime.datetime.now()))


def handle(msg):
    # this is the database to store id to send messge in broadcast
    chat_id = msg['chat']['id']
    command = msg['text']
    
    print "\nCommand " + command + " arrived..."

    if command == '/start':
        bot.sendMessage(
            chat_id, 'This is a Telegram test bot for the group project.')
        # check if the id already exist
        id_check = Users.select(Users.user_id).where(
            Users.user_id == str(chat_id))
        print (id_check)
        if id_check.first() is None:
            add_id(Users(user_id=str(chat_id)))
            bot.sendMessage(chat_id,
                            'Now you are registered and you can receive notifications and control the hydrosys')
        else:
            bot.sendMessage(chat_id, 'You are already registered')

    elif command == '/myid':
        bot.sendMessage(chat_id, chat_id)
    elif command == '/notif':
        text = 'test for notif to: ' + str(chat_id)
        usrlist = Users.select(Users.user_id)
        for user in usrlist:
            print user.user_id
            response = requests.post(
            url='https://api.telegram.org/bot' + TBOT_TOKEN+ '/sendMessage', data={'chat_id': user.user_id, 'text': str(text)}).json()
        bot.sendMessage(user.user_id, str(response['ok']))

    #elif command == '/citeoftheday':
    #    bot.sendMessage(chat_id, 'It Could Work!!!')

    elif command == '/systemstatus' or command == "-System Status-":
        # read the values from the database
        end_time = datetime.datetime.now()
        start_time = datetime.datetime.now() - datetime.timedelta(days=1)

        device_status = dm.get_all_devices()

        device_stats_message = "<b>DEVICE STATUS</b>\n" + device_status[0].name + ": " + \
            device_status[0].state + "\n" + device_status[1].name + ": " + device_status[1].state + "\n===============\n"

        light = dm.get_sensor_stats('light', start_time, end_time)
        light_stats = '[<b>' + light['name'].upper() + '</b>]' + "\nmin: " + str(light['min']) \
            + "\nmax: " + str(light['max']) + "\navg: " + str(light['avg']) + "\nlast: " + str(light['last'])

        dht_humidity = dm.get_sensor_stats(
            'DHT_humidity', start_time, end_time)
        dht_humidity_stats = "[<b>" + dht_humidity['name'].upper() + '</b>]' + "\nmin: " + str(dht_humidity['min']) \
            + "\nmax: " + str(dht_humidity['max']) + "\navg: " + str(dht_humidity['avg']) + "\nlast: " + str(dht_humidity['last'])

        dht_temp = dm.get_sensor_stats('DHT_temp', start_time, end_time)
        dht_temp_stats = '[<b>' + dht_temp['name'].upper() + '</b>]' + "\nmin: " + str(dht_temp['min']) \
            + "\nmax: " + str(dht_temp['max']) + "\navg: " + str(dht_temp['avg']) + "\nlast: " + str(dht_temp['last'])

        water_temp = dm.get_sensor_stats('waterTemp', start_time, end_time)
        water_temp_stats = '[<b>' + water_temp['name'].upper() + '</b>]' + "\nmin: " + str(water_temp['min']) \
            + "\nmax: " + str(water_temp['max']) + "\navg: " + str(water_temp['avg']) + "\nlast: " + str(water_temp['last'])

        # wateflow_current = dm.get_sensor_stats(
        #    'waterFlow_current', start_time, end_time)
        # wateflow_total = dm.get_sensor_stats(
        #  'waterFlow_total', start_time, end_time)

        # {'max': 867.0, 'avg': 524.83, 'last': 764.0, 'name': 'light', 'min': 2.0}

        sensors_stat_message = light_stats + "\n------------------------\n" + dht_humidity_stats + "\n------------------------\n" \
            + dht_temp_stats + "\n------------------------\n" + water_temp_stats

        # str_status = "The " + str(status.name).upper() + " device status is:\n" + "Value: " + \
        #     str(status.value) + "\nTimestamp: " + str(status.timestamp)  
        bot.sendMessage(chat_id, device_stats_message + sensors_stat_message, parse_mode='html')
        print "response of -system status- sent to: " + str(chat_id) + "\n" 

    elif command == '/devicestatus' or command == "-Device Status-":
            # read the values from the database
        end_time = datetime.datetime.now()
        start_time = datetime.datetime.now() - datetime.timedelta(days=1)

        device_status = dm.get_all_devices()

        device_stats_message = "<b>DEVICE STATUS</b> \n<i>" + device_status[0].name + "</i> : " + \
            device_status[0].state + "\n<i>" + device_status[1].name + "</i> : " + device_status[1].state + "\n===============\n"

        # str_status = "The " + str(status.name).upper() + " device status is:\n" + "Value: " + \
        #     str(status.value) + "\nTimestamp: " + str(status.timestamp)
        bot.sendMessage(chat_id, device_stats_message, parse_mode='html')
        print "response of -device status- sent to: " + str(chat_id) + "\n" 

    elif command == '/plantspicture' or command == "-Plant Picture-":
        # it returns the name of the picture taken
        response = requests.get('http://djolez.ddns.net/p5000/camera/take-picture', auth=HTTPBasicAuth(_USER, _PASS))

        # translate the response in json and read the data. Then build the string
        pic_location = PIC_DIR + response.json()["name"]

        print pic_location

        # then send the picture
        bot.sendPhoto(chat_id, open(pic_location, 'rb'))
        print "__picture sent to: " + str(chat_id) + "\n"

    # elif command == '/humidity':
    #     status = dm.get_sensor_last_value('DHT_humidity')
    #     str_status = "The " + str(status.name).upper() + " device status is:\n" + "Value: " + \
    #         str(status.value) + "\nTimestamp: " + str(status.timestamp)
    #     bot.sendMessage(chat_id, str_status)

    # elif command == '/temperature':
    #     status = dm.get_sensor_last_value('DHT_temp')
    #     str_status = "The " + str(status.name).upper() + " device status is:\n" + "Value: " + \
    #         str(status.value) + "\nTimestamp: " + str(status.timestamp)
    #     bot.sendMessage(chat_id, str_status)

    # elif command == '/watertemperature':
    #     status = dm.get_sensor_last_value('waterTemp')
    #     str_status = "The " + str(status.name).upper() + " device status is:\n" + "Value: " + \
    #         str(status.value) + "\nTimestamp: " + str(status.timestamp)
    #     bot.sendMessage(chat_id, str_status)

    # elif command == '/currentwaterflow':
    #     status = dm.get_sensor_last_value('waterFlow_current')
    #     str_status = "The " + str(status.name).upper() + " device status is:\n" + "Value: " + \
    #         str(status.value) + "\nTimestamp: " + str(status.timestamp)
    #     bot.sendMessage(chat_id, str_status)

    # elif command == '/totalwaterflow':
    #     status = dm.get_sensor_last_value('waterFlow_total')
    #     str_status = "The " + str(status.name).upper() + " device status is:\n" + "Value: " + \
    #         str(status.value) + "\nTimestamp: " + str(status.timestamp)
    #     bot.sendMessage(chat_id, str_status)

    elif command == '/help' or command == "-Help-":
        text = "[<b>===INFO===</b>]\nThis bot is developed to monitor an hydroponic system.\n" + \
            "With the command <i>/devicestatus</i>  you can receive information about the status of the devices in the system (light, water pump, etc.)\n" + \
            "Using the command <i>/systemstatus</i> you not only the device status but also some relevations of the sensors(light sensor, humidity, temp, etc.)\n" + \
            "With <i>/plantspicture</i> the bot send a picture of the actual condition of the plants.\nWith <i>/help</i> you open this tips." + \
            "Instead of the commands you can use the virtual keybord and select the action you want."

        keyboardLayout = [["-Device Status-", "-System Status-"], ["-Plant Picture-", "-Help-"]]
        replyKeyboardMakeup = {'keyboard': keyboardLayout, 'resize_keyboard': False, 'one_time_keyboard': False}
        # data = {'chat_id': user_id, 'text': messageText, 'reply_markup': replyKeyboardMakeup}
        # requests.get(REQUEST_URL + "/sendMessage", data=data)
        bot.sendMessage(chat_id, text, parse_mode="html", reply_markup=replyKeyboardMakeup)

bot.message_loop(handle)
print ('I am listening ...')

# Keep the program running.
while 1:
    time.sleep(10)
