from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import mimetypes
import pathlib
import socket
import threading
from datetime import datetime
import json


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)
    
    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        run_client(data)
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()


    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())
    
    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())

UDP_IP = '127.0.0.1'
UDP_PORT = 8080
MESSAGE = "Python Web development exit"

def run_server(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    sock.bind(server)
    # time_ = time.strftime("%F %T")
    
    with open(".\\storage\\data.json", "r") as file:
        date_from_file:dict = json.load(file)
    try:
        while True:
            data, address = sock.recvfrom(1024)
            data_parse = urllib.parse.unquote_plus(data.decode())
            data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
            value = data_dict.get("username")
            sock.sendto(value.encode(), address)
            if value == "exit":
                break
            time_ = str(datetime.now())
            notes_dickt = {time_: data_dict}
            date_from_file.update(notes_dickt)
            with open(".\\storage\\data.json", "w") as file:
                json.dump(date_from_file, file)


    except KeyboardInterrupt:
        print(f'Destroy server')
    finally:
        print("Server UDP SOCKET Closed")
        sock.close()

def run_client(data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = UDP_IP, UDP_PORT
    sock.sendto(data, server)
    response, address = sock.recvfrom(1024)
    if response.decode() == "exit":
        print("HTTP Server")
        exit(0)
    sock.close()



def run(server_class=HTTPServer, handler_class=HttpHandler):

    server = threading.Thread(target=run_server, args=(UDP_IP, UDP_PORT))
    server.start()

    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()

    print('Done!')

if __name__ == '__main__':
    run()