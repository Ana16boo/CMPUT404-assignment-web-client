#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, Anastasia Borissova, https://github.com/tywtyw2002, and https://github.com/treedust
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
    def get_host_port_path(self, url):
        parts = urllib.parse.urlparse(url)
        host = parts.hostname
        port = parts.port
        path = parts.path
        scheme = parts.scheme
        if port is None:
            if scheme == "http":
                port = 80
            else:
                port = 443
        if path == "":
            path = "/"

        return host, port, path

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        code = self.get_headers(data).split()[1]
        return int(code)

    def get_headers(self, data):
        return data.split("\r\n\r\n")[0]

    def get_body(self, data):
        return data.split("\r\n\r\n")[1]

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
        # connect socket
        host, port, path = self.get_host_port_path(url)
        self.connect(host, port)

        # send request and receive response
        request = "GET %s HTTP/1.1\r\n" % path
        request += "Host: %s\r\n"       % host
        request += "User-Agent: curl/7.64.1\r\n"
        request += "Accept: */*\r\n"
        request += "Connection: Close\r\n\r\n"
        self.sendall(request)
        data = self.recvall(self.socket)

        # get code and body
        code = self.get_code(data)
        body = self.get_body(data)

        # close connection
        self.close()
        print(body)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        # connect socket
        host, port, path = self.get_host_port_path(url)
        self.connect(host, port)

        # send request and receive response
        encoded = ""
        if args is None:
            contentLength = str(0)
        else:
            # code from https://stackoverflow.com/questions/5607551/how-to-urlencode-a-querystring-in-python
            encoded += urllib.parse.urlencode(args)
            contentLength = str(len(encoded))

        request = "POST %s HTTP/1.1\r\n"        % path
        request += "Host: %s\r\n"               % host
        request += "Content-Type: application/x-www-form-urlencoded\r\n"
        request += "User-Agent: curl/7.64.1\r\n"
        request += "Accept: */*\r\n"
        request += "Content-Length: %s\r\n\r\n" % contentLength
        request += "%s\r\n"                     % encoded
        request += "Connection: Close\r\n\r\n"

        self.sendall(request)
        data = self.recvall(self.socket)

        # get code and body
        code = self.get_code(data)
        body = self.get_body(data)

        # close connection
        self.close()
        print(body)
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
