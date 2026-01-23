from http.server import SimpleHTTPRequestHandler, HTTPServer
server = HTTPServer(("0.0.0.0", 8080), SimpleHTTPRequestHandler)
server.serve_forever()

