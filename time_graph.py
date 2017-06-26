import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import sqlite3

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
# c.execute("select temperature from temperature where strftime('%d', time) > '22' and strftime('%d', time) < '31'")
# r = c.fetchall()
# temp = []
# for member in r:
#     temp.append(member[0])
c.close()
trace_high = go.Scatter(
                x=time,
                y=hum,
                name = "AAPL High",
                line = dict(color = '#17BECF'),
                opacity = 0.8)

# trace_low = go.Scatter(
#                 x=time,
#                 y=temp,
#                 name = "AAPL Low",
#                 line = dict(color = '#7F7F7F'),
#                 opacity = 0.8)

data = [trace_high]

layout = dict(
    title = "Humidity History",
    xaxis = dict(
        range = ['2017-06-23','2017-06-30'])
)

fig = dict(data=data, layout=layout)
plotly.offline.plot(fig, filename = "Manually Set Range")