import threading
import eventlet
import serial
import subprocess
import os
import csv
import sys
import sqlite3
import plotly
import plotly.plotly as py
import plotly.graph_objs as go

eventlet.monkey_patch()

from flask import Flask, render_template, jsonify, g
from flask_socketio import SocketIO, send, emit
from time import time, gmtime, strftime, sleep

app = Flask(__name__)
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

def listen():
    global ser, data_file
    temp = 0
    hum = 0
    time_taken = []
    min_check = gmtime().tm_min
    test_check = gmtime().tm_min
    hour_check = gmtime().tm_hour
    t_minute_values = []
    h_minute_values = []
    if ser:
        while True:
            if gmtime().tm_min == min_check + 1:
                try:
                    h_minute_values.append(float(split[0]))
                    time_taken.append(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
                except (RuntimeError, TypeError, NameError):
                    print("Could not convert to float!")
                    continue
                try:
                    t_minute_values.append(float(split[1]))
                except (RuntimeError, TypeError, NameError):
                    print("Could not convert to float!")
                    continue
                print (h_minute_values)
                print (t_minute_values)
                min_check = min_check + 1
                sleep(2)
            # if gmtime().tm_hour == hour_check + 1:
            if gmtime().tm_min == test_check + 5:
                hum = hrlyAvg(h_minute_values)
                temp = hrlyAvg(t_minute_values)
                with app.app_context():

                    #Code below for debugging purposes
                    hum_record = get_db().execute('SELECT humidity FROM humidity ORDER BY time DESC')
                    hum = hum_record.fetchall()
                    hum_record.close()
                    f = open('out.txt', w)
                    f.write("\n\n\n\n Latest Humidity Readings")
                    f.write(hum)
                    #Code above for debugging purposes

                    db = get_db()    
                    cur = db.cursor()
                    # read_serial = ser.readline()
                    # print(read_serial)
                    # # read_serial = read_serial.strip()
                    # split = read_serial.split(',');
                    # try:
                    #     h_minute_values.append(float(split[0]))
                    #     time_taken.append(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
                    # except (RuntimeError, TypeError, NameError):
                    #     print("Could not convert to float!")
                    #     continue
                    # try:
                    #     t_minute_values.append(float(split[1]))
                    # except (RuntimeError, TypeError, NameError):
                    #     print("Could not convert to float!")
                    #     continue

                    #Code below for debugging purposes
                    f.write("\n\n\n\n\nValues stored in h_minute_values")
                    f.write(h_minute_values)
                    f.write("\n\n\n\n\nValues stored in t_minute_values")
                    f.write(t_minute_values)
                    f.close()
                    #Code above for debugging purposes

                    time_taken = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                    # print ('Last Entry')
                    # print (h_minute_values[-1])
                    # print (t_minute_values[-1])
                    # if h_minute_values[-1] < 100:
                    cur.execute('INSERT INTO humidity VALUES (?,?)', (time_taken, hum))
                    # if t_minute_values[-1] < 100:
                    cur.execute('INSERT INTO temperature VALUES (?,?)', (time_taken, temp))
                    db.commit()
                    # for row in cur.execute('SELECT * FROM temperature'):
                    #     print ('Temp')
                    #     print (row)
                    # for row2 in cur.execute('SELECT * FROM humidity'):
                    #     print ('Hum')
                    #     print (row2)
                    # hour_check = hour_check + 1
                    test_check = test_check + 5

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/data")
def dataPi():
    temp = 0
    hum = 0
    time_taken = 0
    while True:
        h_records = get_db().execute('SELECT * FROM humidity ORDER BY time DESC')
        hum_single = h_records.fetchone()
        h_records.close()
        hum = hum_single[1]
        t_records = get_db().execute('SELECT * FROM temperature ORDER BY time DESC')
        temp_single = t_records.fetchone()
        t_records.close()
        temp = temp_single[1]

        # Use code below
        # read_serial = ser.readline()
        # print(read_serial)
        # split = read_serial.split(',');
        # if type(float(split[0])) is float:
        #     hum = split[0]
        # else:
        #     continue
        # if type(float(split[1])) is float:
        #     temp = split[1]
        # else:
        #     continue

        time_taken = temp_single[0]
        break
    return render_template('data.html', humidity=hum, temperature=temp, time_taken=time_taken)

@app.route("/sensor_data")
def populateGraph():
    conn = sqlite3.connect("sensor_data.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("select humidity from humidity where strftime('%d', time) > '25' and strftime('%d', time) < '31'")
    r = c.fetchall()
    hum = []
    for member in r:
        hum.append(member[0])
    c.execute("select strftime('%m-%d %H:%M', time) from humidity where strftime('%d', time) > '25' and strftime('%d', time) < '31'")
    r = c.fetchall()
    time = []
    for member in r:
        time.append(member[0])
    c.close()
    trace_high = go.Scatter(
                    x=time,
                    y=hum,
                    name = "AAPL High",
                    line = dict(color = '#17BECF'),
                    opacity = 0.8)
    data = [trace_high]
    layout = dict(
        title = "Humidity History",
        xaxis = dict(
            range = ['2017-06-23','2017-06-30'])
    )

    fig = dict(data=data, layout=layout)
    plotly.offline.plot(fig, filename = "humidity_graph.html")
    return render_template('templates/humidity_graph.html')

def hrlyAvg(data):
    sum = 0
    for entry in data:
        sum += entry
    return sum / len(data)

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
    # if not DATABASE:
    #     print('Initializing db')
    #     init_db()
    print('Starting app')
    app.run(debug=True)
