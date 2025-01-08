#imports
import cv2
from picamera2 import Picamera2
import time
from libcamera import Transform, controls

#pausing or time
time.sleep(0.1) #pauses for 0.1 seconds

#initialize the camera
picam = Picamera2()

still_config = picam.create_still_configuration() #still configuration
video_config = picam.create_video_configuration() #video configuration
preview_config = picam.create_preview_configuration() #preview configuration

#configuration features (uses still as an example, replace with your choice)
still_config = picam.create_still_configuration(main = {"size" : (1280, 720), "format" : RGB888})
still_config = picam.create_still_configuration(transform = Transform(hflip = True, vflip = True) #transform


#using the configurations
picam.configure(preview_config)
picam.configure(still_config)
picam.configure(video_config)

#starting preview window
picam.start_preview(Picamera2.Preview.QTGL, x = 100, y = 200, width = 800, height = 600,
transform = Transform(hflip = 1))
#OR
picam.start_preview(Picamera2.Preview.QTGL)

#camera controls
picam.controls.ExposureTime = 10000
picam.controls.Saturation = 1.0 #can be number from 0.0 to 32.0
picam.controls.Sharpness = 1.0 #can be number from 0.0 to 16.0

#options
picam.options["quality"] = 95 #JPEG quality level- 0 is worst and 95 is best
picam.options["compress_level"] = 2 #PNG compression level, 0 gives no compression, 9 compresses the most and is the slowest

#starting camera
picam.start()

picam.set_controls({"AfMode" : controls.AfModeEnum.Continuous}) #continuously focusing, recommend this
picam.set_controls({"AfMode" : controls.AfModeEnum.Manual, "LensPositions" : 0.0}) #manual focus
#triggering autofocus
job = picam.autofocus_cycle(wait = False)
#some other commands, when you want to make sure autofocus cycle is complete
success = picam.wait(job)

#capturing footage
picam.capture_file('/path/filename.jpg')
#high quality image
picam.capture_file(picamera2.encoders.H264Encoder(), '/path/filename.jpg', quality = picamera2.encoders.Quality.HIGH)

array = picam.capture_array("main") #or "raw", "lores"
image = picam.capture_image("main")
array = picam.switch_mode_and_capture_array(picam.create_still_configuration(), "main")
image = picam.capture_file("image.jpg")

#metadata or EXIF
image, metadata = picam.capture_metadata()
print(metadata)
#OR
print(f"Shutter Speed: {metadata['ExposureTime']}")
print(f"ISO: {metadata['ISO']}")
print(f"Timestamp: {metadata['Timestamp']}")

#image processing
