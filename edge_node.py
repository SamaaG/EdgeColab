#USAGE
# cd \ColabEdge_prtype\edge
# python edge_node.py --image data\2.jpg --yolo \models

import os
import time
import json
import socket
import argparse
from myYOLO import detect
from experiments import appent_exp


def client(args):
	
	# for experiment purposes
	start = time.time()
	exp_list = list()


	detected, tinyolo_predtime = detect(args["image"], args['yolo'], args["confidence"], args["threshold"])
	
	exp_list.append(tinyolo_predtime)

	if not detected:
		#Go to cloud for help
		host = socket.gethostname()  # get local machine name
		port = 8080  # Make sure it's within the > 1024 $$ <65535 range

		
		client_socket = socket.socket()
		client_socket.connect((host, port))

		#  sent the result to the edge
		filename = os.getcwd()
		with client_socket:
			with open(os.path.join(filename, img_name), 'rb') as file:
				sendfile = file.read()
			
			client_socket.sendall(sendfile)
			# print('file sent')

		host = socket.gethostname()   # get local machine name
		port = 8081  # Make sure it's within the > 1024 $$ <65535 range

		soc = socket.socket()
		soc.bind((host,port))
		soc.listen(1)

		# print('waiting for connection...')
		server_socket, adress = soc.accept()
		# print("Connection from: " + str(adress))
		with server_socket:
			recvfile = server_socket.recv(1024)
			detection = json.loads(recvfile)
			# print(detection)
			exp_list.append(detection['cld_time'])
			exp_list.append(detection['yolo_loadtime'])
			exp_list.append(detection['yolo_predtime'])
			
				
	end = time.time()
	# print("[INFO] total process took {:.6f} seconds".format(end - start))
	total_time = end - start
	exp_list.append(total_time)

	appent_exp(exp_list)


if __name__ == '__main__':

	# construct the argument parse and parse the arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--image", required=True,
		help="path to input image")
	ap.add_argument("-y", "--yolo", required=True,
		help="base path to YOLO directory")
	ap.add_argument("-c", "--confidence", type=float, default=0.50,
		help="minimum probability to filter weak detections")
	ap.add_argument("-t", "--threshold", type=float, default=0.3,
		help="threshold when applyong non-maxima suppression")
	args = vars(ap.parse_args())
	client(args)