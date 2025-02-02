import board
from adafruit_lsm6ds.lsm6dsox import LSM6DOX as LSM6DS
from adafruit_lis3mdl import LIS3MDLtff
import time

try:
    accel_gyro = LSM6DS(i2c)
    print("LSM6DS (Accelerometer & Gyroscope) initialized successfully!")
except Exception as e:g6
    print(f"Failed to initialize LSM6DS: {e}")
    accel_gyro = None

try:
    mag = LIS3MDL(i2c)
    print("LIS3MDL (Magnetometer) initialized successfully!")
except Exception as e:
    print(f"Failed to initialize LIS3MDL: {e}")
    mag = None

while True:
    if accel_gyro:
        # Read accelerometer data
        accelx, accely, accelz = accel_gyro.acceleration
        print(f"Accelerometer (m/s^2): X={accelx:.2f}, Y={accely:.2f}, Z={accelz:.2f}")

        # Read gyroscope data
        gyrox, gyroy, gyroz = accel_gyro.gyro
        print(f"Gyroscope (rad/s): X={gyrox:.2f}, Y={gyroy:.2f}, Z={gyroz:.2f}")

    if mag:
        # Read magnetometer data
        magx, magy, magz = mag.magnetic
        print(f"Magnetometer (uT): X={magx:.2f}, Y={magy:.2f}, Z={magz:.2f}")
    time.sleep(1)
