#!/usr/bin/python3

from peewee import *
import datetime

db_proxy = Proxy()

class BaseModel(Model):
    class Meta:
        database = db_proxy

def init_db(file_path = 'db/db.sqlite'):
    db_proxy.initialize(SqliteDatabase(file_path))
    db_proxy.create_tables([Sensor_reading, Device_log, Notification, Users], safe=True)

# for user  #

class Users(BaseModel):
    user_id = CharField()

    class Meta:
        database = db_proxy
    
    def __str__(self):
        return 'ID: {}'.format(self.user_id)
    
    def to_dict(self):
        return self.__dict__['_data']

# ________  #


#########################
#                       #
#   Sensor_reading      #
#                       #
#########################

class Sensor_reading(BaseModel):
    name = CharField()
    value = FloatField()
    timestamp = DateTimeField(default = datetime.datetime.now)
    
    def __str__(self):
        return 'Name: {}, Value: {}, Timestamp: {}'.format(self.name, self.value, self.timestamp) 
    
    def to_dict(self):
        return self.__dict__['_data']

def get_all_sensor_names():
    return Sensor_reading.select(Sensor_reading.name).distinct().order_by(Sensor_reading.name)

def get_all_users():
    return Users.select(Users.user_id)

def add_sensor_reading(sensor_reading):
    db_proxy.connect()
    res = sensor_reading.save()
    db_proxy.close()

def get_sensor_last_value(name):
    return Sensor_reading.select().where((Sensor_reading.name == name)).order_by(Sensor_reading.timestamp.desc()).get()

def get_sensor_stats(name, start, end):
    readings = Sensor_reading.select().where((Sensor_reading.name == name) & (Sensor_reading.timestamp.between(start, end))).order_by(Sensor_reading.timestamp.desc())

    rmin = readings[0].value
    rmax = 0
    rsum = 0
    rlast = 0
    
    for reading in readings:
        if(reading.value < rmin):
            rmin = reading.value
        if(reading.value > rmax):
            rmax = reading.value
        rsum += reading.value

    return {'name': name, 'min': rmin, 'max': rmax, 'avg': round(rsum/len(readings), 2), 'last': (readings[0].value)}


def get_sensor_data(name, start=None, end=None):
    if end is None:
        end = datetime.datetime.now()

    if start is None:
        start = end - datetime.timedelta(hours=1)

    return Sensor_reading.select().where((Sensor_reading.name == name) & (Sensor_reading.timestamp.between(start, end)))

def get_avg_for_sensor(name, start, end):
    readings = get_sensor_data(name, start, end)
    
    if(len(readings) > 0):
        values_sum = 0;
        
        for reading in readings:
            values_sum += reading.value

        return round(values_sum / len(readings), 2)
    else:
        return -1;


#####################
#                   #
#   Device_log      #
#                   #
#####################

class Device_log(BaseModel):
    name = CharField()
    state = CharField()
    timestamp = DateTimeField(default = datetime.datetime.now)
    
    def __str__(self):
        return 'Name: {}, State: {}, Timestamp: {}'.format(self.name, self.state, self.timestamp) 
    
    def to_dict(self):
        return self.__dict__['_data']

def add_device_log(device_log):
    db_proxy.connect()
    res = device_log.save()
    db_proxy.close()

def get_all_devices():
    devices = Device_log.select(Device_log.name).distinct()
    last_states = []

    for device in devices:
        last = Device_log.select().where(Device_log.name == device.name).order_by(Device_log.timestamp.desc()).get()
        last_states.append(last)

    return last_states

def get_device_actions_for_date():
    now = datetime.datetime.now()
    start = now - datetime.timedelta(hours=24)
    
    last_actions = Device_log.select().where(Device_log.timestamp >= start).order_by(Device_log.timestamp.desc())
 
    return last_actions
    

#####################
#                   #
#   Notification    #
#                   #
#####################

class Notification(BaseModel):

    entity = CharField()
    name = CharField()
    message = CharField()
    value = FloatField()
    importance = IntegerField()
    isActive = BooleanField(default = True)
    timestamp = DateTimeField(default = datetime.datetime.now)
    
    def __str__(self):
        return 'Entity: {}, Name: {}, Message: {}, Value: {}, IsActive: {}, Timestamp: {}'.format(self.entity, self.name, self.message, self.value, self.isActive, self.timestamp) 
    
    def to_dict(self):
        return self.__dict__['_data']

def get_all_notifications(active = True):
    return Notification.select().where(Notification.isActive == active)

def add_notification(notification):
    try:
        notif = Notification.select().where((Notification.entity == notification.entity) & (Notification.name == notification.name) & (Notification.isActive == 1)).order_by(Notification.timestamp.desc()).get()
        
    except Notification.DoesNotExist as e:
        print('Adding notification: ', notification)

        db_proxy.connect()
        res = notification.save()
        db_proxy.close()


def deactivate_last_notification(entity, name):

    try:
        notif = Notification.select().where((Notification.entity == entity) & (Notification.name == name) & (Notification.isActive == 1)).order_by(Notification.timestamp.desc()).get()
        print('Deactivating notification for ' + name)

        notif.isActive = False
        db_proxy.connect()
        notif.save()
        db_proxy.close()

    except Notification.DoesNotExist as e:
        pass

























