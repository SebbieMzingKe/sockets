from random import randint
import sys, traceback, threading, socket

from video_stream import VideoStream
from rtp_packet import RtpPacket

class ServerWorker:
	SETUP = 'SETUP'
	PLAY = 'PLAY'
	PAUSE = 'PAUSE'
	TEARDOWN = 'TEARDOWN'
	
	INIT = 0
	READY = 1
	PLAYING = 2
	state = INIT

	OK_200 = 0
	FILE_NOT_FOUND_404 = 1
	CON_ERR_500 = 2
	
	clientInfo = {}
	
	def __init__(self, clientInfo):
		self.clientInfo = clientInfo
		
	def run(self):
		threading.Thread(target=self.recvRtspRequest).start()
	
	def recvRtspRequest(self):
		"""Receive RTSP request from the client."""
		connSocket = self.clientInfo['rtspSocket'][0]
		while True:            
			data = connSocket.recv(256)
			if data:
				print("Data received:\n" + data.decode("utf-8"))
				self.processRtspRequest(data.decode("utf-8"))
	
	# def processRtspRequest(self, data):
	# 	"""Process RTSP request sent from the client."""
	# 	# Get the request type
	# 	request = data.split('\n')
	# 	line1 = request[0].split(' ')
	# 	requestType = line1[0]
		
	# 	# Get the media file name
	# 	filename = line1[1]
		
	# 	# Get the RTSP sequence number 
	# 	seq = request[1].split(' ')
		
	# 	# Process SETUP request
	# 	if requestType == self.SETUP:
	# 		if self.state == self.INIT:
	# 			# Update state
	# 			print("processing SETUP\n")
				
	# 			try:
	# 				self.clientInfo['videoStream'] = VideoStream(filename)
	# 				self.state = self.READY
	# 			except IOError:
	# 				self.replyRtsp(self.FILE_NOT_FOUND_404, seq[1])
				
	# 			# Generate a randomized RTSP session ID
	# 			self.clientInfo['session'] = randint(100000, 999999)
				
	# 			# Send RTSP reply
	# 			self.replyRtsp(self.OK_200, seq[1])
				
	# 			# Get the RTP/UDP port from the last line
	# 			self.clientInfo['rtpPort'] = request[2].split(' ')[3]
		
	# 	# Process PLAY request 		
	# 	elif requestType == self.PLAY:
	# 		if self.state == self.READY:
	# 			print("processing PLAY\n")
	# 			self.state = self.PLAYING
				
	# 			# Create a new socket for RTP/UDP
	# 			self.clientInfo["rtpSocket"] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				
	# 			self.replyRtsp(self.OK_200, seq[1])
				
	# 			# Create a new thread and start sending RTP packets
	# 			self.clientInfo['event'] = threading.Event()
	# 			self.clientInfo['worker']= threading.Thread(target=self.sendRtp) 
	# 			self.clientInfo['worker'].start()
		
	# 	# Process PAUSE request
	# 	elif requestType == self.PAUSE:
	# 		if self.state == self.PLAYING:
	# 			print("processing PAUSE\n")
	# 			self.state = self.READY
				
	# 			self.clientInfo['event'].set()
			
	# 			self.replyRtsp(self.OK_200, seq[1])
		
	# 	# Process TEARDOWN request
	# 	elif requestType == self.TEARDOWN:
	# 		print("processing TEARDOWN\n")

	# 		self.clientInfo['event'].set()
			
	# 		self.replyRtsp(self.OK_200, seq[1])
			
	# 		# Close the RTP socket
	# 		self.clientInfo['rtpSocket'].close()
			
	# def sendRtp(self):
	# 	"""Send RTP packets over UDP."""
	# 	while True:
	# 		self.clientInfo['event'].wait(0.05) 
			
	# 		# Stop sending if request is PAUSE or TEARDOWN
	# 		if self.clientInfo['event'].isSet(): 
	# 			break 
				
	# 		data = self.clientInfo['videoStream'].nextFrame()
	# 		if data: 
	# 			frameNumber = self.clientInfo['videoStream'].frameNbr()
	# 			try:
	# 				address = self.clientInfo['rtspSocket'][1][0]
	# 				port = int(self.clientInfo['rtpPort'])
	# 				self.clientInfo['rtpSocket'].sendto(self.makeRtp(data, frameNumber),(address,port))
	# 			except:
	# 				print("Connection Error")
	# 				#print('-'*60)
	# 				#traceback.print_exc(file=sys.stdout)
	# 				#print('-'*60)


	# def processRtspRequest(self, data):
	# 	"""Process RTSP request sent from the client."""
	# 	# Split the incoming data by lines
	# 	request = data.strip().split('\n')
		
	# 	# Parse the first line to get the request type and filename
	# 	line1 = request[0].split(' ')
	# 	requestType = line1[0]
	# 	filename = line1[1] if len(line1) > 1 else None

	# 	# Parse the sequence number from the second line
	# 	seq = request[1].split(' ') if len(request) > 1 else []
	# 	seq_num = seq[0] if len(seq) > 0 else None

	# 	if not seq_num:
	# 		print("Error: Sequence number is missing in the RTSP request.")
	# 		return

	# 	# Debug logs
	# 	print(f"Parsed Request: {request}")
	# 	print(f"Request Type: {requestType}, Filename: {filename}, Sequence: {seq_num}")

	# 	# Process SETUP request
	# 	if requestType == self.SETUP:
	# 		if self.state == self.INIT:
	# 			print("processing SETUP\n")
	# 			try:
	# 				self.clientInfo['videoStream'] = VideoStream(filename)
	# 				self.state = self.READY
	# 			except IOError:
	# 				self.replyRtsp(self.FILE_NOT_FOUND_404, seq_num)
	def processRtspRequest(self, data):
		"""Process RTSP request sent from the client."""
		# Split request into lines
		request = data.split('\n')
		line1 = request[0].split(' ')
		requestType = line1[0]
		filename = line1[1]

		# Parse the RTSP sequence number safely
		if len(request) > 1:
			seq = request[1].strip().split(' ')  # Strip any whitespace for safety
		else:
			seq = []

		if requestType == self.SETUP:
			if self.state == self.INIT:
				try:
					print(f"Parsed Request: {request}")
					print(f"Request Type: {requestType}, Filename: {filename}, Sequence: {seq[0] if len(seq) > 0 else 'N/A'}")

					# Check if the third line contains the RTP port
					if len(request) > 2 and 'RTP/UDP' in request[2]:
						self.clientInfo['rtpPort'] = int(request[2].split(' ')[3])
					else:
						raise ValueError("RTP port information is missing in the RTSP request.")

					# Initialize video stream
					self.clientInfo['videoStream'] = VideoStream(filename)
					self.state = self.READY

					# Send response
					self.replyRtsp(self.OK_200, seq[0] if len(seq) > 0 else "0")

				except ValueError as e:
					print(f"Error: {e}")
					self.replyRtsp(self.CON_ERR_500, seq[0] if len(seq) > 0 else "0")
				except IOError:
					self.replyRtsp(self.FILE_NOT_FOUND_404, seq[0] if len(seq) > 0 else "0")


					return

				self.clientInfo['session'] = randint(100000, 999999)
				self.replyRtsp(self.OK_200, seq_num)

				# Get the RTP/UDP port from the third line

				# self.clientInfo['rtpPort'] = request[2].split(' ')[3] if len(request) > 2 else None
				
				if len(request) > 2:
					try:
						self.clientInfo['rtpPort'] = request[2].split(' ')[3]
					except IndexError:
						print("Error: RTP port information is missing in the RTSP request.")
						self.replyRtsp(self.CON_ERR_500, seq[1])
						return
				else:
					print("Error: Incomplete RTSP request. RTP port not provided.")
					self.replyRtsp(self.CON_ERR_500, seq[1])
					return


				if not self.clientInfo['rtpPort']:
					print("Error: RTP port is missing in the RTSP request.")
					return

		# Process PLAY request
		elif requestType == self.PLAY:
			if self.state == self.READY:
				print("processing PLAY\n")
				self.state = self.PLAYING

				# Create a new socket for RTP/UDP
				self.clientInfo["rtpSocket"] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

				self.replyRtsp(self.OK_200, seq_num)

				# Create a new thread and start sending RTP packets
				self.clientInfo['event'] = threading.Event()
				self.clientInfo['worker'] = threading.Thread(target=self.sendRtp)
				self.clientInfo['worker'].start()

		# Process PAUSE request
		elif requestType == self.PAUSE:
			if self.state == self.PLAYING:
				print("processing PAUSE\n")
				self.state = self.READY

				self.clientInfo['event'].set()

				self.replyRtsp(self.OK_200, seq_num)

		# Process TEARDOWN request
		elif requestType == self.TEARDOWN:
			print("processing TEARDOWN\n")

			self.clientInfo['event'].set()

			self.replyRtsp(self.OK_200, seq_num)

			# Close the RTP socket
			self.clientInfo['rtpSocket'].close()


	def makeRtp(self, payload, frameNbr):
		"""RTP-packetize the video data."""
		version = 2
		padding = 0
		extension = 0
		cc = 0
		marker = 0
		pt = 26 # MJPEG type
		seqnum = frameNbr
		ssrc = 0 
		
		rtpPacket = RtpPacket()
		
		rtpPacket.encode(version, padding, extension, cc, seqnum, marker, pt, ssrc, payload)
		
		return rtpPacket.getPacket()
		
	def replyRtsp(self, code, seq):
		"""Send RTSP reply to the client."""
		if code == self.OK_200:
			#print("200 OK")
			reply = 'RTSP/1.0 200 OK\nCSeq: ' + seq + '\nSession: ' + str(self.clientInfo['session'])
			connSocket = self.clientInfo['rtspSocket'][0]
			connSocket.send(reply.encode())
		
		# Error messages
		elif code == self.FILE_NOT_FOUND_404:
			print("404 NOT FOUND")
		elif code == self.CON_ERR_500:
			print("500 CONNECTION ERROR")