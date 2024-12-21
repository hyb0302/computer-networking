from socket import *

if __name__ == '__main__':
    serverName = 'localhost'
    serverPort = 12000
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    message = input('Input lowercase sentence:')
    clientSocket.send(message.encode('utf-8'))
    modifiedMessage = clientSocket.recv(1024)
    print('From Server: ', modifiedMessage.decode('utf-8'))
    clientSocket.close()
