import subprocess
import time
import os
from time import sleep
from flask import Flask
from threading import Thread, Lock
from gpio_pins import write_pin
from bme280_sensor import get_bme280_data
import matplotlib.pyplot as plt

LED_PIN = 21

# Bash forloop to ping wbeserver and spike the SoC temp
# for i in {1..10000}; do curl 127.0.0.1:5000; done

def get_shell_command_output(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error executing command: {e}\n{e.stderr}"

class TemperatureThread(Thread):
    def __init__(self, interval: float = 1.0):
        super().__init__()
        self.interval = interval
        self.time_stamps = []
        self.temps = []
        self.running = True
        self.lock = Lock()

    @staticmethod
    def get_temp_f() -> float:
        return float(get_shell_command_output("/usr/bin/vcgencmd measure_temp | awk -F \"[=]\" '{print($2 * 1.8)+32}'"))

    def run(self):
        while self.running:
            with self.lock:
                self.time_stamps.append(time.time())
                self.temps.append(TemperatureThread.get_temp_f())
            sleep(self.interval)
    
    def get_data(self) -> tuple[list,list]:
        with self.lock:
            return list(self.time_stamps), list(self.temps)

    def stop(self):
        self.running = False

app = Flask(__name__)
temp_thread = TemperatureThread(interval=.1)

@app.route('/plot')
def plot():
    # Create a simple plot
    x, y = temp_thread.get_data()
    plt.plot(x, y)

    # Add labels and title (optional)
    plt.xlabel("Time")
    plt.ylabel("Temperature (F)")
    plt.title("RPi5 SoC Temp Plot")

    # Save the plot as a PNG image
    os.makedirs("static", exist_ok=True)
    plt.savefig("static/scatter_plot.png", dpi=300)

    return "<html><img src=/static/scatter_plot.png width=800 height=600></html>"

@app.route('/')
def hello_world():
    tempf, pressure, humidity = get_bme280_data(0x77)
    html = f'<html><h2>Current SoC Temp: {TemperatureThread.get_temp_f()}<h2>'
    html += f'<br><h3>BME 280: Temp F: {tempf:.2f} Pressure: {pressure:.2f} Humidity {humidity:.2f}</h3></html>'
    return html

@app.route('/led/<int:val>')
def show_user_profile(val):
    write_pin(LED_PIN, val > 0)
    return f"Pin {LED_PIN} state {val}"

if __name__ == '__main__':
    temp_thread.start()
    app.run(host='0.0.0.0', port=5000, debug=False)