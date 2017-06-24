import serial
import subprocess

dev = False
ser = False

try:
    dev = subprocess.check_output('ls /dev/ttyACM*', shell=True)
    ser = serial.Serial(dev.strip(), 9600)
except:
    print("Couldn't find any devices.")
s = [0,1]
while True:
	read_serial=ser.readline()
	s[0] = str(ser.readline())
	print s[0]
	print read_serial
