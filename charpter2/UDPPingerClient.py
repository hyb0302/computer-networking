# -*- coding: utf-8 -*-
# @Author: huangyibin
# @Date: 2024/12/29 15:42
# @Description: UDP ping 程序客户端
import socket
from datetime import datetime

server_name = 'localhost'
server_port = 12000
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(1)
for i in range(1, 11):
    start = datetime.now()
    client_socket.sendto(f'Ping {i} {datetime.now()}'.encode('utf-8'), (server_name, server_port))

    try:
        response, server_addr = client_socket.recvfrom(1024)
        end = datetime.now()
        duration = end - start
        print(response.decode('utf-8') + f' RTT: {duration.total_seconds():.2f}s')
    except socket.timeout:
        print(f'Ping {i} Request timed out')
