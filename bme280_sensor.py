import time
import smbus2
import bme280

def celsius_to_fahrenheit(celsius):
    return (celsius * 9/5) + 32

def get_bme280_data(address: int):
    # Initialize I2C bus
    bus = smbus2.SMBus(1)

    # Load calibration parameters
    calibration_params = bme280.load_calibration_params(bus, address)

    try:
        # Read sensor data
        data = bme280.sample(bus, address, calibration_params)

        # Extract temperature, pressure, and humidity
        temperature_celsius = data.temperature
        pressure = data.pressure
        humidity = data.humidity

        # Convert temperature to Fahrenheit
        temperature_fahrenheit = celsius_to_fahrenheit(temperature_celsius)
        return temperature_fahrenheit, pressure, humidity
    except Exception as e:
        print('An unexpected error occurred:', str(e))

def dump_bme280_data(address: int):
    while True:
        try:
            tempf, pressure, humidity = get_bme280_data(address)

            # Print the readings
            print("Temperature: {:.2f} °F".format(tempf))
            print("Pressure: {:.2f} hPa".format(pressure))
            print("Humidity: {:.2f} %".format(humidity))

            # Wait for a few seconds before the next reading
            time.sleep(1)

        except KeyboardInterrupt:
            print('Program stopped')
            break
        except Exception as e:
            print('An unexpected error occurred:', str(e))
            break

if __name__ == "__main__":
    dump_bme280_data()
