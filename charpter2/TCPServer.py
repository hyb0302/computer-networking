from socket import *

if __name__ == '__main__':
    serverPort = 12000
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('', serverPort))
    serverSocket.listen(1)
    print('The server is ready to receive')
    while True:
        connectionSocket, addr = serverSocket.accept()
        message = connectionSocket.recv(1024).decode('utf-8')
        modifiedMessage = message.upper()
        connectionSocket.send(modifiedMessage.encode('utf-8'))
        connectionSocket.close()