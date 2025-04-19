import subprocess
from time import sleep
from flask import Flask

app = Flask(__name__)

def get_shell_command_output(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error executing command: {e}\n{e.stderr}"

def get_temp_f() -> float:
    return float(get_shell_command_output("/usr/bin/vcgencmd measure_temp | awk -F \"[=]\" '{print($2 * 1.8)+32}'"))

@app.route('/')
def hello_world():
    return f'Current Temp: {get_temp_f()}'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)