import cv2
from picamera2 import Picamera2
import time
import board
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX as LSM6DS
from adafruit_lis3mdl import LIS3MDL

picam = Picamera2()
picam.configure(picam.create_still_configuration(main={"size": (1280, 720), "format": "RGB888"}))
#picam.shutter_speed = 1 SETS SHUTTER SPEED TO 1 MILLISECOND
picam.start()

#VARIABLES
THRESHOLD = 10      #Any desired value from the accelerometer

#imu and camera initialization
i2c = board.I2C()
accel_gyro = LSM6DS(i2c)
mag = LIS3MDL(i2c)

def main():
    take_photo()
    
def take_photo():
	while True:
		accelx, accely, accelz = accel_gyro.acceleration
		if accelx>THRESHOLD or accely>THRESHOLD or accelz>THRESHOLD:
			t = time.strftime("_%H%M%S")
			frame = picam.capture_file(f'/home/gladiators/FlatSatImages/test{t}.jpg')
			time.sleep(0.1)
		if cv2.waitKey(1) == ord('q'):
			break

if __name__ == '__main__':
    main()
