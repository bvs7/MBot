#!/usr/bin/python3
from http.server import BaseHTTPRequestHandler as BaseHandler,HTTPServer
#from urlparse import urlparse
import json

ADDRESS = '0.0.0.0'
PORT = '1120'


class MainHandler(BaseHandler):

  def do_GET(self):
    """Serve a GET request, filling in details"""
    print("\nCommand:")
    print(self.command)
    print("\nPath:")
    print(self.path)
    print("\nVersion:")
    print(self.request_version)
    print("\nHeaders:")
    print(self.headers)

    with open("htmltest.html",'r') as f:
      self.respond(f.read())
    f.close()

  def respond(self, html_response):
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()
    self.wfile.write(bytes(html_response, 'UTF-8'))


if __name__ == "__main__":

  server = HTTPServer((ADDRESS, int(PORT)), MainHandler)

  server.serve_forever()
