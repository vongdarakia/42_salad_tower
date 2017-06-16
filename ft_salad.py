import time
import threading
import eventlet
import serial
import subprocess

eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
socketio = SocketIO(app)
num = 0
dev = subprocess.check_output('ls /dev/ttyACM*', shell=True)
ser = serial.Serial(dev.strip(), 9600)

def bg_emit(msg):
    global num, socketio
    num = num + 1
    socketio.emit('my response', num)

def listen():
    global ser
    while ser.inWaiting():
        read_serial=ser.readline()
        print(read_serial)
        bg_emit(read_serial)

@app.route("/")
def index():
    return "Index!"
 
@app.route("/hello")
def hello():
    return render_template(
        'test.html',name=name)
 
@app.route("/members")
def members():
    return "Members"
 
@app.route("/members/<string:name>/")
def getMember(name):
    return render_template(
        'test.html',name=name)

@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)

@socketio.on('my event')
def handle_my_custom_event(json):
    print('received json: ' + str(json))
    socketio.emit('my response', {'data': 'got it!'})

eventlet.spawn(listen)

if __name__ == "__main__":
    # app.run()

    print("running")
    socketio.run(app)
