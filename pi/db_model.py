#!/usr/bin/python3

from peewee import *
import datetime

db_proxy = Proxy()

class BaseModel(Model):
    class Meta:
        database = db_proxy

class Sensor_reading(BaseModel):
    name = CharField()
    value = FloatField()
    timestamp = DateTimeField(default = datetime.datetime.utcnow)
    
    def __str__(self):
        return 'Name: {}, Value: {}, Timestamp: {}'.format(self.name, self.value, self.timestamp) 
    
    def to_dict(self):
        return self.__dict__['_data']

def add_sensor_reading(sensor_reading):
    db_proxy.connect()
    res = sensor_reading.save()
    db_proxy.close()

def init_db(file_path = 'db/db.sqlite'):
    db_proxy.initialize(SqliteDatabase(file_path))
    db_proxy.create_tables([Sensor_reading], safe=True)

def get_sensor_data(name, start=None, end=None):
    if end is None:
        end = datetime.datetime.utcnow()

    if start is None:
        start = end - datetime.timedelta(hours=1)
        print('Start date: ', start)

    return Sensor_reading.select().where((Sensor_reading.name == name) & (Sensor_reading.timestamp.between(start, end)))


