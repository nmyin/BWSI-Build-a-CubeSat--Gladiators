#Copy, delete, move images
import shutil
import os
#Health Check
import board
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX as LSM6DS
from adafruit_lis3mdl import LIS3MDL
import time
import math
import psutil
#Server
import os
import ssl
import logging
from http.server import SimpleHTTPRequestHandler, HTTPServer
from functools import partial
#Threading
import threading
#Image comparison
import cv2
import numpy as np
from skimage.metrics import structural_similarity
#Camera
from picamera2 import Picamera2

#FIELD VARIABLES for HEALTH CHECK
i2c = board.I2C()
rot_x, rot_y, rot_z = 0, 0, 0
bigG = 6.6743015
mass = 5.97237
t1 = 0
t2 = 0
accel_gyro = LSM6DS(i2c)

#FIELD VARIABLES for SERVER
alt= ""
ori= ""
temp= ""
batt= ""
IMAGE_FOLDER = '/home/gladiators/storing_images/downlink'
SERVER_ADDRESS = ('192.168.1.25', 8000)
CERT_FILE = '/home/gladiators/Code/server.pem'
KEY_FILE = '/home/gladiators/Code/server.key'
USERNAME = 'gladiators'
PASSWORD = 'GlutiousMaximus'

#FIELD VARIABLES for CAMERA
picam = Picamera2()
picam.configure(picam.create_still_configuration(main={"size": (4608, 2592 ), "format": "RGB888"}))

class SharedData:
    def __init__(self):
        self.lock = threading.Lock()
        self.alt = ""
        self.ori = ""
        self.temp = ""
        self.batt = ""

    def update(self, alt, ori, temp, batt):
        with self.lock:
            self.alt = alt
            self.ori = ori
            self.temp = temp
            self.batt = batt

    def get(self):
        with self.lock:
            return self.alt, self.ori, self.temp, self.batt

shared_data = SharedData()

#________________HEALTH CHECK_________________

def altitude():
    global bigG, mass
    accelx, accely, accelz = accel_gyro.acceleration
    accelx = accelx + 0.35
    accely = accely + 1.12
    #print(f"Accelerometer (m/s^2): X={accelx:.2f}, Y={accely:.2f}, Z={accelz:.2f}")
    acc_total = math.sqrt(accelx**2 + accely**2 + accelz**2)
    level = altitude_is_cool(6371, acc_total)
    if (level):
        return 'Altitude: good'
    else:
        return f'Altitude: BAD, {math.sqrt((bigG * mass * 10**7) / acc_total)}'
		
def altitude_is_cool(al, accel):
    acc = bigG * mass *10**7 /(al**2)
    if accel > acc - 0.05 and accel < acc + 0.5:
        return True
    return False
    
def orientation():
    global t1, t2, rot_x, rot_y, rot_z
    gyro_x, gyro_y, gyro_z = accel_gyro.gyro
    t2 = time.time()
    dt = t2-t1
    t1 = t2
    rot_x = rot_x + gyro_x*dt
    rot_y = rot_y + gyro_y*dt
    rot_z = rot_z + gyro_z*dt
    #print(f"Angular Velocity (rad/s): X={gyro_x:.2f}, Y={gyro_y:.2f}, Z={gyro_z:.2f}")
    orient = orientation_is_cool(rot_x, rot_y, rot_z)
    if (orient):
        return "Orientation: good"
    else:
        return f"Orientation: BAD (radians: X={rot_x:.2f}, Y={rot_y:.2f}, Z={rot_z:.2f})"
    
def orientation_is_cool(rot_x, rot_y, rot_z):
    if (abs(rot_x) >=0.2 or abs(rot_y) >=0.2 or abs(rot_z) >=0.2):
        return False
    return True

def temperature():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as file:
        temperature = int(file.read()) / 1000.0
        if (temperature >= 30 and temperature <= 50):
            return f"Temperature: {temperature}"
        else:
            return f"Temperature: BAD- {temperature}"

def battery():
    battery = psutil.sensors_battery()
    if battery is not None:
        return f"Battery: {battery.percent}"
    else:
        return "Battery: cannot read"
        
def health_check():
	global alt, ori, temp, batt, t1
	alt= altitude()
	ori= orientation()
	temp= temperature()
	batt= battery()
	shared_data.update(alt, ori, temp, batt)
		
#__________SERVER______________

os.chdir(IMAGE_FOLDER)

logging.basicConfig(filename='server.log', level=logging.INFO, format='%(asctime)s - %(message)s')

class SecureHTTPRequestHandler(SimpleHTTPRequestHandler):
    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm="Cubesat Server"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()
    
    def do_GET(self):
        global IMAGE_FOLDER, SERVER_ADDRESS, CERT_FILE, KEY_FILE, USERNAME, PASSWORD
        alt, ori, temp, batt = shared_data.get()

        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html_content = f"""
            <html lang="en">
            <head>
                <meta charset="utf-8">
                <title>Cubesat Image Server</title>
                <meta http-equiv="refresh" content="1"><!--Auto-refresh every 1 second -->
            </head>
            <body>
                <h1>Cubesat Image Server</h1>
                <p>{alt}</p>
                <p>{ori}</p>
                <p>{temp}</p>
                <p>{batt}</p>
                <a href="/images">View images</a>
            </body>
            </html>
            """
            self.wfile.write(html_content.encode())

        elif self.path == '/images':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            image_files = os.listdir(IMAGE_FOLDER)
            html_content = "<html><body><h1>Images</h1><ul>"
            
            for image_file in image_files:
                image_path = f'/images/{image_file}'
                html_content += f'<li><a href="{image_path}">{image_file}</a></li>'
            
            html_content += "</ul></body></html>"
            self.wfile.write(html_content.encode())

        elif self.path.startswith('/images/'):
            image_name = self.path[8:]
            image_path = os.path.join(IMAGE_FOLDER, image_name)

            if os.path.exists(image_path) and os.path.isfile(image_path):
                self.send_response(200)
                self.send_header('Content-Type', 'image/tiff')
                self.end_headers()

                with open(image_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, 'File not found')

        else:
            super().do_GET()

    def is_authenticated(self, auth_header):
        global USERNAME, PASSWORD
        import base64
        auth_decoded = base64.b64decode(auth_header.split(' ')[1]).decode('utf-8')
        return auth_decoded == f"{USERNAME}:{PASSWORD}"

def run_server():
    global IMAGE_FOLDER, SERVER_ADDRESS, CERT_FILE, KEY_FILE, USERNAME, PASSWORD
    handler = partial(SecureHTTPRequestHandler)
    httpd = HTTPServer(SERVER_ADDRESS, handler)
    
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    logging.info(f"Serving images from {IMAGE_FOLDER} securely at https://{SERVER_ADDRESS[0]}:{SERVER_ADDRESS[1]}/")
    print(f"Server running at https://{SERVER_ADDRESS[0]}:{SERVER_ADDRESS[1]}/")
    print("Press Ctrl+C to stop the server.")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logging.info("Server stopped.")
        print("Server stopped.")
        httpd.server_close()
        
#________IMAGES__________

def copy(initial, final):
    filename = os.path.basename(initial)
    destination_path = os.path.join(final, filename)
    shutil.copy(initial, destination_path)
    print(f"Image copied to: {destination_path}")

def delete(image_path):
    os.remove(image_path)
    print(f"Image deleted: {image_path}")

def move(initial, final):
    filename = os.path.basename(initial)
    destination_path = os.path.join(final, filename)
    shutil.move(initial, destination_path)
    print(f"Image moved to: {destination_path}")

def orb_sim(img1, img2):
    orb = cv2.ORB_create()
    kp_a, desc_a = orb.detectAndCompute(img1, None)
    kp_b, desc_b = orb.detectAndCompute(img2, None)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(desc_a, desc_b)
    similar_regions = [i for i in matches if i.distance < 50]
    if len(matches) == 0:
        return 0
    return len(similar_regions) / len(matches)

def structural_sim(img1, img2):
    img1 = img1.astype(np.float32)
    img2 = img2.astype(np.float32)
    similarity_scores = []
    for i in range(3):
        channel1 = img1[:, :, i]
        channel2 = img2[:, :, i]
        sim = structural_similarity(channel1, channel2, full=False)
        similarity_scores.append(sim)
    return np.mean(similarity_scores)
	
def img_process(i):
	global picam
	picam.capture_file(f'/home/gladiators/storing_images/current/{i}.tiff')
	if not os.path.isfile(os.path.join('/home/gladiators/storing_images/previous', f'{i}.tiff')):
		move(f'/home/gladiators/storing_images/current/{i}.tiff', f'/home/gladiators/storing_images/previous')
	else:
		img1 = cv2.imread(f'/home/gladiators/storing_images/previous/{i}.tiff')
		img2 = cv2.imread(f'/home/gladiators/storing_images/current/{i}.tiff')
		obs = orb_sim(img1, img2)
		structure = structural_sim(img1, img2)
		if obs <= 0.15 or structure <= 0.025:
			copy(f'/home/gladiators/storing_images/current/{i}.tiff', f'/home/gladiators/storing_images/downlink')
			os.rename(f'/home/gladiators/storing_images/downlink/{i}.tiff', f'/home/gladiators/storing_images/downlink/before{i}.tiff')
			copy(f'/home/gladiators/storing_images/previous/{i}.tiff', f'/home/gladiators/storing_images/downlink')
			os.rename(f'/home/gladiators/storing_images/downlink/{i}.tiff', f'/home/gladiators/storing_images/downlink/after{i}.tiff')
		delete(f'/home/gladiators/storing_images/previous/{i}.tiff')
		move(f'/home/gladiators/storing_images/current/{i}.tiff', f'/home/gladiators/storing_images/previous')
        
#__________THREADING_____________    
class IMUThread(threading.Thread):
    def __init__(self, read_imu_function):
        threading.Thread.__init__(self)
        self.read_imu_function = read_imu_function
        self.is_running = True

    def run(self):
        while self.is_running:
            self.read_imu_function()
            time.sleep(0.1)

    def stop(self):
        self.is_running = False

class ServerThread(threading.Thread):
    def __init__(self, server_function):
        threading.Thread.__init__(self)
        self.server_function = server_function
        self.is_running = True

    def run(self):
        while self.is_running:
            self.server_function()
            time.sleep(0.5)

    def stop(self):
        self.is_running = False

class ImageThread(threading.Thread):
    def __init__(self, image_function):
        threading.Thread.__init__(self)
        self.image_function = image_function
        self.is_running = True
    def run(self):
        i = 0
        while self.is_running:
            self.image_function(i)
            time.sleep(30)
            i = i+1

    def stop(self):
        self.is_running = False

def main():
	global t1, picam
	t1 = time.time()
	
	imu_thread = IMUThread(health_check)
	imu_thread.daemon = True
	imu_thread.start()
	
	server_thread = ServerThread(run_server)
	server_thread.daemon = True
	server_thread.start()
	
	picam.start()
	
	image_thread = ImageThread(img_process)
	image_thread.daemon = True
	image_thread.start()
	
	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		print("Exiting...")
		server_thread.stop()
		imu_thread.stop()
		imu_thread.join()
		server_thread.join()

if __name__ == "__main__":
    main()
