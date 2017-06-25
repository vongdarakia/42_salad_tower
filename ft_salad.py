import threading
import eventlet
import serial
import subprocess
import os
import csv
import sys
import sqlite3

eventlet.monkey_patch()

from flask import Flask, render_template, jsonify, g
from flask_socketio import SocketIO, send, emit
from time import time, gmtime, strftime, sleep

app = Flask(__name__)
# socketio = SocketIO(app)
fieldnames = ['temperature', 'humidity', 'time']
data = []
data_file = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "sensor_data.csv"
)

output_logs = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "output.logs"
)

DATABASE = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "sensor_data.db"
)

# sys.stdout = open(output_logs, 'w+')

def get_db():
    # with app.app_context():
    db = getattr(g, "_database", None)
    if db is None:
        print ('db is None')
        db = g._database = sqlite3.connect(DATABASE)
        print ('Connection established')
    return db

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as file:
            db.cursor().executescript(file.read())
        db.commit()

# @app.cli.command('initdb')
# def initdb_command():
#     init_db()
#     print('Database initialized')

def listen():
    global ser, data_file
    tmp = 0
    hum = 0
    time_taken = 0
    checkpoint = gmtime().tm_min
    t_minute_values = []
    h_minute_values = []
    with app.app_context():
        db = get_db()    
        cur = db.cursor()
        if ser:
            while True:
                if gmtime().tm_min == checkpoint + 1:
                    read_serial = ser.readline()
                    print(read_serial)
                    # read_serial = read_serial.strip()
                    split = read_serial.split(',');
                    if type(float(split[0])) is float:
                        h_minute_values.append(float(split[0]))
                    else:
                    #     raise ValueError, "Not a float"
                        continue
                    if type(float(split[1])) is float:
                        t_minute_values.append(float(split[1]))
                    else:
                    #     raise ValueError, "Not a float"
                        continue
                    print (h_minute_values)
                    print (t_minute_values)
                    cur.execute('INSERT INTO humidity VALUES (?,?,?)', (1,time_taken, h_minute_values[-1]))
                    cur.execute('INSERT INTO temperature VALUES (?,?,?)', (1,time_taken, t_minute_values[-1]))
                    db.commit()
                    cur.execute('SELECT * FROM humidity, temperature')
                    print (cur.fetchone())

                    # if len(split) != 2:
                    #     continue

                    # if 'Humidity' in split[0]:
                    #     hum_data = split[0].split(' ');
                    #     if (len(hum_data) != 2):
                    #         continue
                    #     hum = hum_data[1]
                    # else:
                    #     continue

                    # if 'Temperature' in split[1]:
                    #     tmp_data = split[1].split(' ');
                    #     if (len(tmp_data) != 2):
                    #         continue
                    #     tmp = tmp_data[1]
                    # else:
                    #     continue

                    # time_taken = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                    # appendDataCSV(data_file, makeData(hum, tmp, time_taken));
                    checkpoint = checkpoint + 1
                    sleep(2)
            # else:
            #     print ('Not time')
            #     print (gmtime().tm_min)
            #     print (gmtime().tm_sec)
    print("listening over")

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/data")
def dataPi(sensorData=None):
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
                continue

            if 'Humidity' in split[0]:
                hum_data = split[0].split(' ');
                if (len(hum_data) != 2):
                    continue
                hum = hum_data[1]
            else:
                continue

            if 'Temperature' in split[1]:
                tmp_data = split[1].split(' ');
                if (len(tmp_data) != 2):
                    continue
                tmp = tmp_data[1]
            else:
                continue

            time_taken = strftime("%Y-%m-%d %H:%M:%S", gmtime())
            break
    sensorData=makeData(hum, tmp, time_taken)
    return render_template('data.html', humidity=hum, temperature=tmp, time_taken=time_taken)

@app.route("/sensor_data")
def getSensorData():
    global data
    return jsonify(data[-43200:])

def createDataCSV(filename):
    with open(filename, 'w+') as csvfile:
        fieldnames = ['temperature', 'humidity', 'time']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

def appendDataCSV(filename, data):
    with open(filename, 'a+') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow(data)

def makeData(humidity, temperature, time):
    return {
        'temperature': temperature,
        'humidity': humidity,
        'time': time
    }

def hrlyAvg(data):
    index = 0
    while (index < len(data)):
        print('Here')
        print(data[index]['time'])
        time_stamp = data[index]['time']
        parsed_stamp = time_stamp.split(' ')
        hour = parsed_stamp[1]
        print(hour) 
        index += 1

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        print ('Closing Connection')
        db.close()

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
    hrlyAvg(data)
    init_db()
    app.run(debug=True)
    #socketio.run(app, debug=True)
