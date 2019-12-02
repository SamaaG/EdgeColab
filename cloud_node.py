#USAGE
# cd Desktop\UCSC_Courses\DataSys\EdgeColab_repo\ColabEdge_prtype\cloud

import os
import cv2
import json
import time
import socket
from myYOLO_c import detect


def server():

	# derive the paths to the YOLO weights and model configuration
	weightsPath = os.path.sep.join(['models', "yolov3.weights"])
	configPath = os.path.sep.join(['models', "yolov3.cfg"])

	# load our YOLO object detector trained on COCO dataset (80 classes)
	print("[INFO] loading YOLO from disk...")
	start1 = time.time()
	net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)
	end1 = time.time()

	while True:
		host = socket.gethostname()   # get local machine name
		port = 8080  # Make sure it's within the > 1024 $$ <65535 range

		soc = socket.socket()
		soc.bind((host,port))
		soc.listen(1)
		detection = None
		print('waiting for connection...')

		server_socket, adress = soc.accept()
		start = time.time()
		print("Connection from: " + str(adress))
		with server_socket:
			with open("detect_img.jpg",'wb') as file:
				print("recieving...")
				while True:
					recvfile = server_socket.recv(4096)
					if not recvfile: 
						break
					file.write(recvfile)

			print("File has been received.")

			detection = detect("detect_img.jpg", "models", net)


		host = socket.gethostname()  # get local machine name
		port = 8081  # Make sure it's within the > 1024 $$ <65535 range

		client_socket = socket.socket()
		client_socket.connect((host, port))
		end = time.time()
		print("[INFO] cloud took {:.6f} seconds".format(end - start))
		detection['cld_time'] = end - start
		detection['yolo_loadtime'] = end1 - start1
		with client_socket:
			client_socket.sendall(json.dumps(detection).encode())
			print('file sent')
	

if __name__ == '__main__':
 	server()