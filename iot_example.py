# Kyriazis Ioannis 3212018107

import matplotlib.pyplot as plt
from matplotlib import style
from matplotlib.widgets import Button
from threading import Timer
from datetime import datetime
import paho.mqtt.client as mqtt
import ssl
import os
import sys

class IoTExample:
    def __init__(self):
        self.ax = None
        self._establish_mqtt_connection()
        self._prepare_graph_window()

    # call this method to start the client loop
    def start(self):
        if self.ax:
            self.client.loop_start()
            plt.show()
        else:
            self.client.loop_forever()
      
    # call this method to disconnect from the broker
    def disconnect(self, args=None):
        self.client.disconnect() # disconnect

    # You need to fill this in, here we will place the commands
    # For connecting to the broker
    def _establish_mqtt_connection(self):
        self.client = mqtt.Client()
        print("Trying to connect to MQTT server...")
        self.client.tls_set_context(ssl.SSLContext(ssl.PROTOCOL_TLSv1_2))
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_log = self._on_log
        self.client.username_pw_set('iotlesson', '***')
        self.client.connect('***', 8883)


    # This is the callback that will be called after the connection is
    # established
    def _on_connect(self, client, userdata, flags, rc):
        if rc==0:
            print("Connected OK Returned code=",rc)
            self.client.subscribe('hscnl/hscnl02/state/ZWaveNode005_Switch/state')
            self.client.subscribe('hscnl/hscnl02/state/ZWaveNode005_ElectricMeterWatts/state')
            self.client.subscribe('hscnl/hscnl02/command/ZWaveNode005_Switch/command')

            self.client.subscribe('hscnl/hscnl02/state/ZWaveNode006_Switch/state')
            self.client.subscribe('hscnl/hscnl02/state/ZWaveNode006_ElectricMeterWatts/state')
            self.client.subscribe('hscnl/hscnl02/command/ZWaveNode006_Switch/command')
            
        else:
            print("Bad connection Returned code=",rc)



    # This is the callback that will be called whenever a new log
    # event is created
    def _on_log(self, client, userdata, level, buf):
        print('log: ', buf)


    def _prepare_graph_window(self):
        # Plot variables
        plt.rcParams['toolbar'] = 'None'
        fig=plt.figure()
        self.dataX = []
        self.dataY = []
        self.ax = fig.add_subplot(121)
        self.first_ts = datetime.now()
        self.lineplot, = self.ax.plot(self.dataX, self.dataY, linestyle='--', marker='o', color='b')
        self.ax.figure.canvas.mpl_connect('close_event', self.disconnect)
        self.finishing = False
        self._my_timer()


        self.dataXX = []
        self.dataYY = []
        self.ax1 = fig.add_subplot(122)
        self.first_ts1 = datetime.now()
        self.lineplot1, = self.ax1.plot(self.dataXX, self.dataYY, linestyle='--', marker='o', color='r')
        self.ax1.figure.canvas.mpl_connect('close_event', self.disconnect)
        self.finishing1 = False
        self._my_timer1()

        axcut = plt.axes([0.0, 0.0, 0.1, 0.06])
        self.bcut = Button(axcut, 'ON')
        axcut2 = plt.axes([0.1, 0.0, 0.1, 0.06])
        self.bcut2 = Button(axcut2, 'OFF')
        self.state_field = plt.text(1.2, 0.3, 'Node005')
        self.bcut.on_clicked(self._button_on_clicked)
        self.bcut2.on_clicked(self._button_off_clicked)

        axcut1 = plt.axes([0.6, 0.0, 0.1, 0.06])
        self.bcut1 = Button(axcut1, 'ON')
        axcut21 = plt.axes([0.7, 0.0, 0.1, 0.06])
        self.bcut21 = Button(axcut21, 'OFF')
        self.state_field = plt.text(1.2, 0.3, 'Node006')
        self.bcut1.on_clicked(self._button_on_clicked1)
        self.bcut21.on_clicked(self._button_off_clicked1)


    def _refresh_plot(self):
        if len(self.dataX) > 0:
            self.ax.set_xlim(min(self.first_ts, min(self.dataX)), max(max(self.dataX), datetime.now()))
            self.ax.set_ylim(min(self.dataY) * 0.8, max(self.dataY) * 1.2)
            self.ax.relim()
        else:
            self.ax.set_xlim(self.first_ts, datetime.now())
            self.ax.relim()
        plt.draw()

    def _refresh_plot1(self):
        if len(self.dataXX) > 0:
            self.ax1.set_xlim(min(self.first_ts1, min(self.dataXX)), max(max(self.dataXX), datetime.now()))
            self.ax1.set_ylim(min(self.dataYY) * 0.8, max(self.dataYY) * 1.2)
            self.ax1.relim()
        else:
            self.ax1.set_xlim(self.first_ts1, datetime.now())
            self.ax1.relim()
        plt.draw()

    def _add_value_to_plot(self, value): 
        self.dataX.append(datetime.now()) 
        self.dataY.append(value) 
        self.lineplot.set_data(self.dataX, self.dataY) 
        self._refresh_plot()

    def _add_value_to_plot1(self, value): 
        self.dataXX.append(datetime.now()) 
        self.dataYY.append(value) 
        self.lineplot1.set_data(self.dataXX, self.dataYY) 
        self._refresh_plot1()


    def _my_timer(self):
        self._refresh_plot()
        if not self.finishing:
            Timer(1.0, self._my_timer).start()

    def _my_timer1(self):
        self._refresh_plot1()
        if not self.finishing1:
            Timer(1.0, self._my_timer1).start()

    # This is the callback that will be called whenever a new message
    # is received
    def _on_message(self, client, userdata, msg):
        if msg.topic == 'hscnl/hscnl02/state/ZWaveNode005_ElectricMeterWatts/state':
            self._add_value_to_plot(float(msg.payload))
        elif msg.topic == 'hscnl/hscnl02/state/ZWaveNode006_ElectricMeterWatts/state':
            self._add_value_to_plot1(float(msg.payload))
        print(msg.topic+' '+str(msg.payload))



    def _button_on_clicked(self, event):
        self.client.publish('hscnl/hscnl02/sendcommand/ZWaveNode005_Switch', 'ON')

    def _button_off_clicked(self, event):
        self.client.publish('hscnl/hscnl02/sendcommand/ZWaveNode005_Switch', 'OFF')

    def _button_on_clicked1(self, event):
        self.client.publish('hscnl/hscnl02/sendcommand/ZWaveNode006_Switch', 'ON')

    def _button_off_clicked1(self, event):
        self.client.publish('hscnl/hscnl02/sendcommand/ZWaveNode006_Switch', 'OFF')



try:
    iot_example = IoTExample()
    iot_example.start()
except KeyboardInterrupt:
    print("Interrupted")
    try:
        iot_example.disconnect()
        sys.exit(0)
    except SystemExit:
        os._exit(0)