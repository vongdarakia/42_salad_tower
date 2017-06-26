import sqlite3

conn = sqlite3.connect("sensor_data.db")
conn.row_factory = sqlite3.Row
c = conn.cursor()
c.execute("select humidity from humidity where strftime('%d', time) > '22' and strftime('%d', time) < '31'")
# c.execute("DELETE FROM humidity where strftime('%d', time) = '27'")
r = c.fetchall()
hum = []
for member in r:
	hum.append(member[0])
c.execute("select strftime('%d %H:%M', time) from humidity where strftime('%d', time) > '27' and strftime('%d', time) < '31'")
r = c.fetchall()
time = []
for member in r:
	time.append(member[0])
print (hum)
print (time)
# conn.commit()
c.close()