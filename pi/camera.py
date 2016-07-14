import picamera
from time import sleep
from datetime import datetime

img_location = '../web-app/img/'
timelapse_location = img_location + 'timelapse/'

def take_picture(config=None):    
    picture_name = 'image' + str(datetime.now()) + '.jpg'

    with picamera.PiCamera() as camera:
        if config:
            for key, value in config.iteritems():
                print(key, value, camera, img_location, picture_name)
                setattr(camera, key, value)
        
        #camera.resolution = (1920, 1080)
        sleep(2)
        camera.capture(img_location + picture_name)
        return picture_name


def take_timelapse(config=None):
    picture_name = 'timelapse' + str(datetime.now()) + '.jpg'

    with picamera.PiCamera() as camera:
        camera.resolution = (1920, 1080)
        sleep(2)
        camera.capture(timelapse_location + picture_name, quality=7)
        return picture_name

