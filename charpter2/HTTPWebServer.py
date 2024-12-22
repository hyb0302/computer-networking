# -*- coding: utf-8 -*-
# @Author: huangyibin
# @Date: 2024/12/21 14:00:00
# @Description: 自顶向下第二章作业1：web http 服务器，返回查询的文件，文件不存在时返回404

import mimetypes
import os
import datetime
import socket
import sys
import textwrap
import itertools
import logging


class HTTPWebServer(object):
    DEFAULT_CONTENT_TYPE = 'application/octet-stream'

    def __init__(self, directory=os.getcwd(), port=80):
        self.directory = directory
        self.port = port
        self.server_info = self.get_server_info()
        self.server_socket = None
        logging.basicConfig(level=logging.INFO)

    def get_server_info(self):
        return (f"huangyibin's http server "
                f"Python version {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

    def startup(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('', self.port))
        self.server_socket.listen(5)
        logging.info('The web server is ready to receive')
        try:
            while True:
                connection_socket, addr = self.server_socket.accept()
                logging.info(f'The connection is established, address: {addr}')
                self.handle_request(connection_socket, addr)
                connection_socket.close()
                logging.info(f'The connection is closed, address: {addr}')
        except KeyboardInterrupt:
            logging.info("\nServer interrupted by user. Shutting down...")
        finally:
            self.shutdown()

    def handle_request(self, connection_socket, address):
        # 解析HTTP请求
        http_method, url, http_version, request_headers = self.read_request(connection_socket)
        if not url:
            self.send_http_404_response(connection_socket)
            return

        # 查找文件
        file_path = self.get_file_path(url)
        if not os.path.isfile(file_path):
            self.send_http_404_response(connection_socket)
            return

        # 获取文件信息
        file_stat = os.stat(file_path)

        # 检测文件是否已修改
        if self.is_not_modified(request_headers, file_stat):
            self.send_http_304_response(connection_socket)
            return

        self.send_file_response_header(connection_socket, file_path, file_stat)
        self.send_file_response_body(connection_socket, file_path)

    def read_request(self, connection_socket):
        request_message = connection_socket.recv(4096).decode('utf-8')
        request_lines = request_message.splitlines()
        if not request_lines:
            return None
        http_method, url, http_version = self.read_status_line(request_lines)
        request_headers = self.read_request_headers(request_lines)
        return http_method, url, http_version, request_headers

    def read_status_line(self, request_lines):
        status_line = request_lines[0]
        logging.info(f"Status Line: {status_line}")
        try:
            (http_method, url, http_version) = status_line.split(' ')
        except ValueError as e:
            logging.info(f"Error parsing request line: {e}")
            return None, None, None
        except Exception as e:
            logging.info(f"Unexpected error: {e}")
            return None, None, None
        return http_method, url, http_version

    def read_request_headers(self, request_lines):
        header_lines = list(itertools.takewhile(lambda x: x != "", request_lines[1:]))
        request_headers = {
            key.lower(): value.strip()
            for key, value in (line.split(":", 1) for line in header_lines if ":" in line)
        }
        return request_headers

    def send_http_404_response(self, connection_socket):
        connection_socket.send(self.build_http_response('404 Not Found').encode('utf-8'))

    def build_http_response(self, status, extra_headers=None):
        response = f"""
            HTTP/1.1 {status}
            Content-Type: text/html
            Connection: close
            Server: {self.server_info}
            Date: {self.get_current_http_date()}

        """
        if extra_headers:
            response += extra_headers
        return textwrap.dedent(response)

    def get_file_path(self, url):
        return os.path.join(self.directory, *url.split('/'))

    def is_not_modified(self, request_headers, file_stat):
        if 'if-modified-since' in request_headers:
            modified_since = request_headers['if-modified-since']
            logging.debug(f'modified_since:{modified_since}')
            try:
                request_time = datetime.datetime.strptime(modified_since, '%a, %d %b %Y %H:%M:%S GMT')
            except ValueError:
                return False
            logging.debug(f'request_time:{request_time}')
            return request_time >= datetime.datetime.fromtimestamp(file_stat.st_mtime).replace(microsecond=0)

    def send_http_304_response(self, connection_socket):
        connection_socket.send(self.build_http_response('304 Not Modified').encode('utf-8'))

    def send_file_response_header(self, connection_socket, file_path, file_stat):
        connection_socket.send(self.build_http_file_response_header(file_path, file_stat).encode('utf-8'))

    def build_http_file_response_header(self, file_path, file_stat):
        response = f"""
        HTTP/1.1 200 OK
        Connection: close
        Date: {self.get_current_http_date()}
        Server: {self.server_info}
        Content-Type: {self.get_content_type(file_path)}
        Content-Length: {file_stat.st_size}
        Last-Modified: {self.format_http_date(datetime.datetime.fromtimestamp(file_stat.st_mtime))}

        """
        return textwrap.dedent(response)

    def get_current_http_date(self):
        return self.format_http_date(datetime.datetime.now())

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
        logging.info('The web server is shutting down')
        if self.server_socket:
            self.server_socket.close()


if __name__ == '__main__':
    server = HTTPWebServer()
    server.startup()
