import mimetypes
import os
from datetime import datetime
from socket import *
import sys
import textwrap


class HTTPWebServer(object):

    DEFAULT_CONTENT_TYPE = 'application/octet-stream'

    def __init__(self, directory=os.getcwd(), port=80):
        self.directory = directory
        self.port = port
        self.server_info = self.get_server_info()

    def get_server_info(self):
        return (f"huangyibin's http server "
                f"Python version {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

    def startup(self):
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.bind(('', self.port))
        self.server_socket.listen(5)
        print('The web server is ready to receive')
        while True:
            connection_socket, addr = self.server_socket.accept()
            print(f'The connection is established, address: {addr}')
            self.handle_request(connection_socket, addr)
            connection_socket.close()
            print(f'The connection is closed, address: {addr}')

    def handle_request(self, connection_socket, address):
        # 解析HTTP请求
        url = self.read_url(connection_socket)
        if not url:
            self.send_http_404_response(connection_socket)
            return

        # 查找文件
        file_path = self.get_file_path(url)
        if not os.path.isfile(file_path):
            self.send_http_404_response(connection_socket)
            return

        self.send_file_response_header(connection_socket, file_path)
        self.send_file_response_body(connection_socket, file_path)

    def read_url(self, connection_socket):
        request_message = connection_socket.recv(2048).decode('utf-8')
        request_lines = request_message.splitlines()
        if not request_lines:
            return None
        status_line = request_message.splitlines()[0]
        print(f"Status Line: {status_line}")
        try:
            (http_method, url, http_version) = status_line.split(' ')
        except ValueError as e:
            print(f"Error parsing request line: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
        return url

    def send_http_404_response(self, connection_socket):
        connection_socket.send(self.build_http_404_response().encode('utf-8'))

    def build_http_404_response(self):
        response = f"""
            HTTP/1.1 404 Not Found
            Content-Type: text/html
            Connection: close
            Server: {self.server_info}
        """
        return textwrap.dedent(response)

    def get_file_path(self, url):
        return os.path.join(self.directory, *url.split('/'))

    def send_file_response_header(self, connection_socket, file_path):
        connection_socket.send(self.build_http_file_response_header(file_path).encode('utf-8'))

    def build_http_file_response_header(self, file_path):
        file_stat = os.stat(file_path)
        response = f"""
        HTTP/1.1 200 OK
        Connection: close
        Date: {self.get_current_http_date()}
        Server: {self.server_info}
        Content-Type: {self.get_content_type(file_path)}
        Content-Length: {file_stat.st_size}
        Last-Modified: {self.format_http_date(datetime.fromtimestamp(file_stat.st_mtime))}

        """
        return textwrap.dedent(response)

    def get_current_http_date(self):
        return self.format_http_date(datetime.now())

    def format_http_date(self, date):
        return date.strftime('%a, %d %b %Y %H:%M:%S GMT')

    def get_content_type(self, file_path):
        content_type, _ = mimetypes.guess_type(file_path)
        return content_type or self.DEFAULT_CONTENT_TYPE

    def send_file_response_body(self, connection_socket, file_path):
        with open(file_path, 'rb') as file:
            chunk = file.read(1024)
            while chunk:
                connection_socket.send(chunk)
                chunk = file.read(1024)

    def shutdown(self):
        print('The web server is shutting down')
        if self.server_socket:
            self.server_socket.close()


if __name__ == '__main__':
    server = HTTPWebServer()
    try:
        server.startup()
    finally:
        server.shutdown()