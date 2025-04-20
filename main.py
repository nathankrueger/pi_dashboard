import subprocess
import time
from time import sleep
from flask import Flask
from threading import Thread, Lock
import matplotlib.pyplot as plt

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
    plt.savefig("static/scatter_plot.png", dpi=300)

    return "<html><img src=/static/scatter_plot.png width=800 height=600></html>"

@app.route('/')
def hello_world():
    return f'Current Temp: {TemperatureThread.get_temp_f()}'

if __name__ == '__main__':
    temp_thread.start()
    app.run(host='0.0.0.0', port=5000, debug=False)