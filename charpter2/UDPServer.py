from socket import *

if __name__ == '__main__':
    serverPort = 12000
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('', serverPort))
    print('The server is ready to receive')
    while True:
        message, clientAddr = serverSocket.recvfrom(2048)
        modifiedMessage = message.decode("utf-8").upper()
        serverSocket.sendto(modifiedMessage.encode(), clientAddr)
