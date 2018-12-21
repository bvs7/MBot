#!/usr/bin/python3
from http.server import BaseHTTPRequestHandler as BaseHandler,HTTPServer

import json

ADDRESS = '0.0.0.0'
PORT = '1120'


class MainHandler(BaseHandler):

  def do_GET(self):
    try:
      length = int(self.headers['Content-Length'])
      content = self.rfile.read(length).decode('utf-8')
      request = json.loads(content)

      print("\nHeaders:")
      print(self.headers)
      print("\nContent:")
      print(content)
      print("\nRequest:")
      print(request)
    except Exception as e:
      print("\nEXCEPTION: {}".format(e))

    return

if __name__ == "__main__":

  server = HTTPServer((ADDRESS, int(PORT)), MainHandler)

  server.serve_forever()