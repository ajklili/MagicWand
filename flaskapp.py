import matplotlib as mpl
mpl.use('Agg')
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import math
import matplotlib.pyplot as plt
plt.ioff()


import pickle
import thread
import os
import json
import time
import requests
import logging
import sys
MAX = sys.maxsize

from flask import Flask, request, render_template, make_response, Response, send_file

from flask_pymongo import PyMongo
from pymongo import MongoClient

from bson import json_util
from bson.json_util import dumps, loads


app = Flask(__name__)
mongoDefault = PyMongo(app)
app.config['MONGO2_DBNAME'] = 'wand'
mongo = PyMongo(app, config_prefix='MONGO2')
imagesDirectoryPath = '/home/ubuntu/flaskapp/images/'
#server_ip = str(requests.get('https://api.ipify.org').text)
server_ip = '54.91.116.127'


@app.route('/file/')
def savefile():
    with open('/home/ubuntu/flaskapp/images/testtestfile.txt', 'w') as f:  # need directiory permission
        f.write('abc')
    return 'ok!'


@app.route('/saveip/')
def saveip():
    dip = request.remote_addr
    mongo.db.ip.insert({'ip': dip})
    return 'OK'


@app.route('/ttt/', methods=['POST'])
def test():
    string = request.data
    string = string.replace('\'', '"')
    jsondata = json.loads(string)
    databasetest = mongo.db.test
    databasetest.insert(jsondata)
    return string


@app.route("/")
def hello():
    server_ip = requests.get('https://api.ipify.org').text
    return 'Magic Wand!'


@app.route('/test/', methods=['POST'])
def savepoi():
    herelat=40.807983
    herelon=-73.962028
    data_string = request.data  # raw data from Pi
    data_string = data_string.replace('\'', '"')
    data_json = json.loads(data_string)
    #data_json = {'uid': 1, 'geolocation': {'lon': -73.96411,'lat': 40.807722, 'alt': 100.0}, 'sensordata': [{'x': 1}, {'x': 2}]}

    # parse metadata
    userId = data_json['uid']
    timestamp = time.time()
    timeString = time.asctime(time.localtime(time.time()))
    longitude = float(data_json['geolocation']['lon'])
    latitude = float(data_json['geolocation']['lat'])
    try:
        altitude = float(data_json['geolocation']['alt'])
    except:
        altitude = 100
    sensor_string = data_json['sensordata']
    sensor_string = sensor_string[0:len(sensor_string) - 1]
    sensor_list = sensor_string.split('/')
    # create a image from raw data
    imageFileName = str(hash(str(userId) + ',' + str(timestamp)) % MAX)
    # with open('/home/ubuntu/flaskapp/images/testtestfile.txt', 'w') as f:  # need directiory permission
    #     pickle.dump(sensor_list, f)
    thread.start_new_thread(createImage, (imageFileName, sensor_list))
    # save the poi into database:pois
    longitude=herelon
    latitude=herelat
    doodle = {'id': int(timestamp), 'name': 'User'+str(userId), 'description': timeString, 'longitude': longitude,
              'latitude': latitude, 'altitude': altitude, 'imageName': imageFileName}
    database = mongo.db.testpois
    database.insert(doodle)
    return 'Saved!'


@app.route('/getpois/')
def getpois():
    args = request.args
    if len(args) < 2:
        return 'geolocation required but not given'
    # get user location
    lat = float(args.get('lat'))
    lon = float(args.get('lon'))
    mongo.db.usergeolocation.insert({'lat': lat, 'lon': lon})
    # choose pois in a certain range
    radius = 1
    pois_json = findPois(lon, lat)
    pois_data = dumps(pois_json)
    response = make_response(pois_data)
    #response.headers['Access-Control-Allow-Origin'] = '*'
    return response


def createImage(imageFileName, data_list):
    acccx = []
    acccy = []
    acccz = []
    for line in data_list:
        line = line.split(',')
        acccx.append(float(line[3]))
        acccy.append(float(line[4]))
        acccz.append(float(line[5]))

    ###Start###
    a = acccx[:50]
    X0 = sum(acccx[:50]) / 50
    Y0 = sum(acccy[:50]) / 50
    Z0 = sum(acccz[:50]) / 50
    accx = []
    accy = []
    accz = []
    for i in range(0, len(acccx)):
        accx.append(acccx[i] - X0)
        accy.append(acccy[i] - Y0)
        accz.append(acccz[i] - Z0)

    Vx = []
    Vy = []
    Vz = []
    for i in range(0, len(accx)):
        Vx.append(np.trapz(accx[:i]))
        Vy.append(np.trapz(accy[:i]))
        Vz.append(np.trapz(accz[:i]))

    MoveX = 2 * np.trapz(Vx) / (len(Vx) * len(Vx))
    MoveY = 2 * np.trapz(Vy) / (len(Vy) * len(Vy))

    for i in range(0, len(Vx)):
        Vx[i] = Vx[i] - MoveX * i
        Vy[i] = Vy[i] - MoveY * i
        Vz[i] = Vz[i] - Vz[len(Vz) - 1] * i / len(Vz)
    x = []
    y = []
    z = []
    for i in range(0, len(Vx)):
        x.append(np.trapz(Vx[:i]))
        y.append(np.trapz(Vy[:i]))
        z.append(np.trapz(Vz[:i]))
    ###End###
    mpl.rcParams['figure.figsize']=(1,1)
    plt.plot(x, y)
    plt.axis('off')
    plt.savefig(('/home/ubuntu/flaskapp/images/' + imageFileName + '.png'),format='png',transparent=True)

    # save image file to images/filename
    return imageFileName


def findPois(lon, lat):
    # using testing database
    # pois center: lat=40.807722, lon=-73.96411, total=40
    radius = 0.05  # 1 degree about 100km
    database = mongo.db.testpois
    lon1 = lon - radius
    lon2 = lon + radius
    lat1 = lat - radius
    lat2 = lat + radius
    # filter: field and range
    pois_json = database.find(
        {"longitude": {"$gt": lon1, "$lt": lon2}, "latitude": {"$gt": lat1, "$lt": lat2}})
    pois_json = json.loads(dumps(pois_json))
    for j in pois_json:
        j['imageurl'] = 'http://' + server_ip + \
            '/getimage/' + j['imageName'] + '/'

    return pois_json


@app.route('/getimage/<imagename>/')
def getimage(imagename):
    filename = 'images/' + imagename + '.png'
    return send_file(filename, mimetype='image/png')


if __name__ == "__main__":
    app.run(debug=True)
