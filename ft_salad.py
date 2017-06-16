import time
import threading
import eventlet
import serial
import subprocess
import csv

eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
socketio = SocketIO(app)
num = 0
fieldnames = ['temperature', 'temperature_time', 'humidity', 'humidity_time']
data_file = "data.csv"
data = []

def bg_emit(msg):
    global num, socketio
    num = num + 1
    socketio.emit('my response', num)

def listen():
    global ser
    if (ser):
        while True:
            read_serial=ser.readline()
	    print("printing: ")
            print(read_serial.strip())            
            # bg_emit(read_serial)
    print("done")

@app.route("/")
def index():
    return render_template('index.html')
 
@app.route("/members/<string:name>/")
def getMember(name):
    return render_template(
        'test.html',name=name)

def createDataCSV(filename):
    with open(filename, 'w') as csvfile:
        fieldnames = ['temperature', 'temperature_time', 'humidity', 'humidity_time']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

def appendDataCSV(filename, data):
    with open(filename, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow(data)

def makeData(temperature, temperature_time, humidity, humidity_time):
    return {
        'temperature': temperature,
        'temperature_time': temperature_time,
        'humidity': humidity,
        'humidity_time': humidity_time
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
