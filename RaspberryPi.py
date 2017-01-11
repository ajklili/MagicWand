# Distributed with a free-will license.
# Use it any way you want, profit or free, provided it fits in the licenses of its associated works.
# LSM9DS0
# This code is designed to work with the LSM9DS0_I2CS I2C Mini Module available from ControlEverything.com.
# https://www.controleverything.com/content/Accelorometer?sku=LSM9DS0_I2CS#tabs-0-product_tabset-2

import smbus
import time
import requests
import RPi.GPIO as GPIO
import time
import serial
import pynmea2
import threading


# Get I2C bus
bus = smbus.SMBus(1)

# LSM9DS0 Gyro address, 0x6B(106)
# Select control register1, 0x20(32)
#        0x0F(15)    Data rate = 95Hz, Power ON
#                    X, Y, Z-Axis enabled
bus.write_byte_data(0x6B, 0x20, 0x0F)
# LSM9DS0 address, 0x6B(106)
# Select control register4, 0x23(35)
#        0x30(48)    DPS = 2000, Continuous update
bus.write_byte_data(0x6B, 0x23, 0x30)
# LSM9DS0 Accl and Mag address, 0x1D(30)
# Select control register1, 0x20(32)
#        0x67(103)    Acceleration data rate = 100Hz, Power ON
#                    X, Y, Z-Axis enabled
bus.write_byte_data(0x1D, 0x20, 0x67)
# LSM9DS0 Accl and Mag address, 0x1D(30)
# Select control register2, 0x21(33)
#        0x18(24)    Full scale = +/-8g
bus.write_byte_data(0x1D, 0x21, 0x18)
# LSM9DS0 Accl and Mag address, 0x1D(30)
# Select control register5, 0x24(36)
#        0x70(112)    Magnetic high resolution, Output data rate = 50Hz
bus.write_byte_data(0x1D, 0x24, 0x70)
# LSM9DS0 Accl and Mag address, 0x1D(30)
# Select control register6, 0x25(37)
#        0x60(96)    Magnetic full scale selection = +/-12 gauss
bus.write_byte_data(0x1D, 0x25, 0x60)
# LSM9DS0 Accl and Mag address, 0x1D(30)
# Select control register7, 0x26(38)
#        0x00(00)    Normal mode, Magnetic continuous conversion mode
bus.write_byte_data(0x1D, 0x26, 0x00)


time.sleep(0.01)


def readdata():

    # LSM9DS0 Gyro address, 0x6B(106)
    # Read data back from 0x28(40), 2 bytes
    # X-Axis Gyro LSB, X-Axis Gyro MSB
    data0 = bus.read_byte_data(0x6B, 0x28)
    data1 = bus.read_byte_data(0x6B, 0x29)

    # Convert the data
    xGyro = data1 * 256 + data0
    if xGyro > 32767:
        xGyro -= 65536
    GYROX = xGyro * 0.07000

    # LSM9DS0 Gyro address, 0x6B(106)
    # Read data back from 0x2A(42), 2 bytes
    # Y-Axis Gyro LSB, Y-Axis Gyro MSB
    data0 = bus.read_byte_data(0x6B, 0x2A)
    data1 = bus.read_byte_data(0x6B, 0x2B)

    # Convert the data
    yGyro = data1 * 256 + data0
    if yGyro > 32767:
        yGyro -= 65536
    GYROY = yGyro * 0.07000

    # LSM9DS0 Gyro address, 0x6B(106)
    # Read data back from 0x2C(44), 2 bytes
    # Z-Axis Gyro LSB, Z-Axis Gyro MSB
    data0 = bus.read_byte_data(0x6B, 0x2C)
    data1 = bus.read_byte_data(0x6B, 0x2D)

    # Convert the data
    zGyro = data1 * 256 + data0
    if zGyro > 32767:
        zGyro -= 65536
    GYROZ = zGyro * 0.07000

    # LSM9DS0 Accl and Mag address, 0x1D(30)
    # Read data back from 0x28(40), 2 bytes
    # X-Axis Accl LSB, X-Axis Accl MSB
    data0 = bus.read_byte_data(0x1D, 0x28)
    data1 = bus.read_byte_data(0x1D, 0x29)

    # Convert the data
    xAccl = data1 * 256 + data0
    if xAccl > 32767:
        xAccl -= 65536
    ACCX = xAccl * 0.244 / 1000 * 9.80665

    # LSM9DS0 Accl and Mag address, 0x1D(30)
    # Read data back from 0x2A(42), 2 bytes
    # Y-Axis Accl LSB, Y-Axis Accl MSB
    data0 = bus.read_byte_data(0x1D, 0x2A)
    data1 = bus.read_byte_data(0x1D, 0x2B)

    # Convert the data
    yAccl = data1 * 256 + data0
    if yAccl > 32767:
        yAccl -= 65536
    ACCY = yAccl * 0.244 / 1000 * 9.80665

    # LSM9DS0 Accl and Mag address, 0x1D(30)
    # Read data back from 0x2C(44), 2 bytes
    # Z-Axis Accl LSB, Z-Axis Accl MSB
    data0 = bus.read_byte_data(0x1D, 0x2C)
    data1 = bus.read_byte_data(0x1D, 0x2D)

    # Convert the data
    zAccl = data1 * 256 + data0
    if zAccl > 32767:
        zAccl -= 65536
    ACCZ = zAccl * 0.244 / 1000 * 9.80665

    # LSM9DS0 Accl and Mag address, 0x1D(30)
    # Read data back from 0x08(08), 2 bytes
    # X-Axis Mag LSB, X-Axis Mag MSB
    data0 = bus.read_byte_data(0x1D, 0x08)
    data1 = bus.read_byte_data(0x1D, 0x09)

    # Convert the data
    xMag = data1 * 256 + data0
    if xMag > 32767:
        xMag -= 65536
    MAGX = xMag * 0.48 / 1000

    # LSM9DS0 Accl and Mag address, 0x1D(30)
    # Read data back from 0x0A(10), 2 bytes
    # Y-Axis Mag LSB, Y-Axis Mag MSB
    data0 = bus.read_byte_data(0x1D, 0x0A)
    data1 = bus.read_byte_data(0x1D, 0x0B)

    # Convert the data
    yMag = data1 * 256 + data0
    if yMag > 32767:
        yMag -= 65536
    MAGY = yMag * 0.48 / 1000

    # LSM9DS0 Accl and Mag address, 0x1D(30)
    # Read data back from 0x0C(12), 2 bytes
    # Z-Axis Mag LSB, Z-Axis Mag MSB
    data0 = bus.read_byte_data(0x1D, 0x0C)
    data1 = bus.read_byte_data(0x1D, 0x0D)

    # Convert the data
    zMag = data1 * 256 + data0
    if zMag > 32767:
        zMag -= 65536
    MAGZ = zMag * 0.48 / 1000
    return(GYROX, GYROY, GYROZ, ACCX, ACCY, ACCZ, MAGX, MAGY, MAGZ)


serialPort = serial.Serial("/dev/ttyUSB0", 9600, timeout=0.5)

lon = 0.
lat = 0.
alt = 0.
lon_dir = 0.
lat_dir = 0.
alt_unit = 0.
timestamp = 0.


def readGPS():
    global lon
    global lat
    global alt
    global lon_dir
    global lat_dir
    global alt_unit
    global timestamp
    while True:
        str = serialPort.readline()

        if str.find('GGA') > 0:
            msg = pynmea2.parse(str)
            lon = msg.longitude
            lat = msg.latitude
            alt = msg.altitude
            lon_dir = msg.lon_dir
            lat_dir = msg.lat_dir
            alt_unit = msg.altitude_units
            timestamp = msg.timestamp
        time.sleep(.1)


gps_thread = threading.Thread(target=readGPS)
gps_thread.start()

if(__name__ == '__main__'):

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(23, GPIO.OUT)
    while 1:
        # print('waiting')
        input_state = GPIO.input(18)
        acc = ''
        t = 0
        if input_state == False:
            GPIO.output(23, GPIO.HIGH)
            # print('button pushed')
            print "Times: %s - Lat: %s %s - Lon: %s %s - Altitude: %s %s" % (timestamp, lat, lat_dir, lon, lon_dir, alt, alt_unit)

            start = time.time()
            while 1:
                t += 1
                input_state = GPIO.input(18)
                GYROX, GYROY, GYROZ, ACCX, ACCY, ACCZ, MAGX, MAGY, MAGZ = readdata()
                # print "%s,%s,%s,%s,%s,%s,%s,%s,%s"
                # %(GYROX,GYROY,GYROZ,ACCX,ACCY,ACCZ,MAGX,MAGY,MAGZ)
                acc += str(GYROX) + ',' + str(GYROY) + ',' + str(GYROZ) + ',' + str(ACCX) + ',' + str(
                    ACCY) + ',' + str(ACCZ) + ',' + str(MAGX) + ',' + str(MAGY) + ',' + str(MAGZ) + '/'
                # time.sleep(0.0005)
                if input_state == True:

                    end = time.time()
                    GPIO.output(23, GPIO.LOW)
                    print "%s-------%s--------%s---------------------------" % (t, end - start, (end - start) / t)
                    break
            accread = str(acc)
            accreadpos = {'uid': 1, 'geolocation': {'lon': str(
                lat), 'lat': str(lon), 'alt': str(alt)}, 'sensordata': accread}
            # print(accread)
            r = requests.post('http://54.91.116.127/test/',
                              data=str(accreadpos))
            print(r.text)
