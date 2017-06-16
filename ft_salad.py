import threading
import eventlet
import serial
import subprocess
import csv
import datetime

eventlet.monkey_patch()

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, send, emit
from time import time, gmtime, strftime

app = Flask(__name__)
socketio = SocketIO(app)
num = 0
fieldnames = ['temperature', 'humidity', 'time']
data_file = "sensor_data.csv"
data = []

def bg_emit(msg):
    global num, socketio
    num = num + 1
    socketio.emit('my response', num)

def listen():
    global ser
    tmp = 0
    hum = 0
    time_taken = 0

    if ser:
        while True:
            read_serial = ser.readline()
            print(read_serial)
            read_serial = read_serial.strip()
            split = read_serial.split(',');

            if len(split) != 2:
                print(len(split))
                continue

            if 'Humidity' in split[0]:
                hum_data = split[0].split(' ');
                if (len(hum_data) == 2):
                    hum = hum_data[1]
                else:
                    continue
            else:
		print('no humidity')
                continue

            if 'Temperature' in split[1]:
                tmp_data = split[1].split(' ');
                if (len(tmp_data) == 2):
                    tmp = tmp_data[1]
                else:
                    continue
            else:
		print('no temp')
                continue

            time_taken = strftime("%Y-%m-%d %H:%M:%S", gmtime())
            appendDataCSV(data_file, makeData(hum, tmp, time_taken));         
    print("listening over")

@app.route("/")
def index():
    return render_template('index.html')
 
#@app.route("/members/<string:name>/")
#def getMember(name):
#    return render_template(
#        'test.html',name=name)

@app.route("/sensor_data")
def getSensorData():
    global data
    return jsonify(data[-43200:])

def createDataCSV(filename):
    with open(filename, 'w') as csvfile:
        fieldnames = ['temperature', 'humidity', 'time']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

def appendDataCSV(filename, data):
    with open(filename, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow(data)

def makeData(humidity, temperature, time):
    return {
        'temperature': temperature,
        'humidity': humidity,
        'time': time
    }

dev = False
ser = False
try:
    dev = subprocess.check_output('ls /dev/ttyACM*', shell=True)
    ser = serial.Serial(dev.strip(), 9600)
except:
    print("Couldn't find any devices.")

eventlet.spawn(listen)

if __name__ == "__main__":
    try:
        with open(data_file) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(row)
                print(row)
    except:
        createDataCSV(data_file)

    row_count = sum(1 for row in data)

    if (row_count == 0):
        createDataCSV(data_file)

    # print makeData(1, 1, 2, 2)
    # appendDataCSV(data_file, {'temperature': 1, 'temperature_time': 1, 'humidity': 2, 'humidity_time': 2});
        # print(data)
    # with open('names.csv', 'rb') as csvfile:
    #     fieldnames = ['first_name', 'last_name']
    #     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    #     writer.writeheader()
    #     writer.writerow({'first_name': 'Baked', 'last_name': 'Beans'})
    #     writer.writerow({'first_name': 'Lovely', 'last_name': 'Spam'})
    #     writer.writerow({'first_name': 'Wonderful', 'last_name': 'Spam'})
    socketio.run(app, debug=False)
