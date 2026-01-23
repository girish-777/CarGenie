from http.server import SimpleHTTPRequestHandler, HTTPServer
import os
os.chdir("/data")
server = HTTPServer(("0.0.0.0", 8080), SimpleHTTPRequestHandler)
server.serve_forever()

