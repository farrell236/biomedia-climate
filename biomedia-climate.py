#!/usr/bin/env python
import bme680
import time
import datetime
import urllib.request as urllib2

# Enter Your API key here
myAPI = 'THINGSPEAK_API_KEY' 
# URL where we will send the data, Don't change it
baseURL = 'https://api.thingspeak.com/update?api_key=%s' % myAPI 

print("""Display Temperature, Pressure, Humidity and Gas

Press Ctrl+C to exit

""")

try:
    sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
except IOError:
    sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

# These calibration data can safely be commented
# out, if desired.

print('Calibration data:')
for name in dir(sensor.calibration_data):

    if not name.startswith('_'):
        value = getattr(sensor.calibration_data, name)

        if isinstance(value, int):
            print('{}: {}'.format(name, value))

# These oversampling settings can be tweaked to
# change the balance between accuracy and noise in
# the data.

sensor.set_humidity_oversample(bme680.OS_2X)
sensor.set_pressure_oversample(bme680.OS_4X)
sensor.set_temperature_oversample(bme680.OS_8X)
sensor.set_filter(bme680.FILTER_SIZE_3)
sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)

print('\n\nInitial reading:')
for name in dir(sensor.data):
    value = getattr(sensor.data, name)

    if not name.startswith('_'):
        print('{}: {}'.format(name, value))

sensor.set_gas_heater_temperature(320)
sensor.set_gas_heater_duration(150)
sensor.select_gas_heater_profile(0)

# Up to 10 heater profiles can be configured, each
# with their own temperature and duration.
# sensor.set_gas_heater_profile(200, 150, nb_profile=1)
# sensor.select_gas_heater_profile(1)

print('\n\nPolling:')
try:
    temp = pres = humi = airq = 0  # init values
    while True:
        if sensor.get_sensor_data():

            # Read sensor values
            temp = sensor.data.temperature
            pres = sensor.data.pressure
            humi = sensor.data.humidity
            if sensor.data.heat_stable:
                airq = sensor.data.gas_resistance

            # Print data to terminal
            output = '{0:.2f} C,{1:.2f} hPa, {2:.2f} %RH, {3:.2f} Ohms'.format(
                temp, pres, humi, airq)
            print(output)

            # Log data to file
            f = open('climate.txt','a+')
            output = '{},{},{},{},{}\r\n'.format(
                datetime.datetime.now(), temp, pres, humi, airq)
            f.write(output)
            f.close()

            try:
                # Sending the data to thingspeak
                conn = urllib2.urlopen(
                    baseURL + '&field1=%s&field2=%s&field3=%s&field4=%s' % (temp, pres, humi, airq))
                print(conn.read())
                # Closing the connection
                conn.close()
            except urllib2.URLError as e:
                print(e.reason)

        time.sleep(60)

except KeyboardInterrupt:
    pass
    