#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
	print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
	def __init__(self, code=200, body=""):
		self.code = code
		self.body = body

class HTTPClient(object):
	#def get_host_port(self,url):

	def connect(self, host, port):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect((host, port))
		return None

	def get_code(self, data):
		split_data = data.split()
		#print("Code Split_Data: ", split_data)


		status_code = None
		if (len(split_data) > 0):
			status_code = int(split_data[1])
		return status_code

	def get_headers(self,data):
		split_data = data.split("\r\n\r\n")
		headers = None
		if (len(split_data) >= 1):
			headers = split_data[0]		
		return headers

	def get_body(self, data):
		split_data = data.split("\r\n\r\n")
		#print("Body Split_Data: ", split_data)
		body = None
		if (len(split_data) >= 2):
			body = split_data[1]
		return body

	def sendall(self, data):
		self.socket.sendall(data.encode('utf-8'))

	def close(self):
		self.socket.close()

	# read everything from the socket
	def recvall(self, sock):
		buffer = bytearray()
		done = False
		while not done:
			part = sock.recv(1024)
			if (part):
				buffer.extend(part)
			else:
				done = not part
		return buffer.decode('utf-8')

	def GET(self, url, args=None):
		code = 500
		body = ""
		ParseResults = urllib.parse.urlparse(url)
		#print(ParseResults)


		path = ParseResults.path
		if (path == ""):
			path = "/"
		
		query = ParseResults.query
		if (query != ""):
			path = path + "?" + query



		host = ParseResults.hostname
		port = ParseResults.port
		if (port == None):
			port = 80

		#print("HOST: ", host)
		#print("PORT: ", port)

		self.connect(host, port)
		
		request = "GET " + path + " HTTP/1.1\r\nHOST: " + host + "\r\n\r\n"  
		#print("REQUEST: ", request) 
		

		self.sendall(request)
		response = self.recvall(self.socket)
		self.close()
		code = self.get_code(response)
		body = self.get_body(response)
		#print("Code: " + str(code) + " Body: " + str(body))

		return HTTPResponse(code, body)

	def POST(self, url, args=None):
		code = 500
		body = ""
		ParseResults = urllib.parse.urlparse(url)
		path = ParseResults.path
		if (path == ""):
			path = "/"
		
		query = ParseResults.query
		if (query != ""):
			path = path + "?" + query


		host = ParseResults.hostname
		port = ParseResults.port
		if (port == None):
			port = 80

		self.connect(host, port)

		content = ""
		if (args != None):
			for key in args.keys():
				content += str(key) + "=" + str(args[key]) + "&"
			content = content[:-1]
		
		contentLength = str(len(content))
		


		request = "POST {} HTTP/1.1\r\nHost: {}\r\n".format(path, host) + \
				"Content-Type: application/x-www-form-urlencoded" + "\r\n" + \
				"Content-Length: {}\r\n\r\n{}\r\n\r\n".format(contentLength, content)  
		print("REQUEST: ", request) 

		self.sendall(request)
		response = self.recvall(self.socket)
		self.close()

		code = self.get_code(response)
		body = self.get_body(response)

		
		#print("Code: " + str(code) + " Body: " + str(body))
		
		return HTTPResponse(code, body)

	def command(self, url, command="GET", args=None):
		if (command == "POST"):
			return self.POST( url, args )
		else:
			return self.GET( url, args )

if __name__ == "__main__":
	client = HTTPClient()
	command = "GET"
	if (len(sys.argv) <= 1):
		help()
		sys.exit(1)
	elif (len(sys.argv) == 3):
		print(client.command( sys.argv[2], sys.argv[1] ))
	else:
		print(client.command( sys.argv[1] ))
