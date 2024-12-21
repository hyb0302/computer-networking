from socket import *

if __name__ == '__main__':
    serverName = 'localhost'
    serverPort = 12000
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    message = input('Input lowercase sentence:')
    clientSocket.sendto(message.encode('utf-8'), (serverName, serverPort))
    modifiedMessage, serverAddr = clientSocket.recvfrom(2048)
    print(modifiedMessage.decode('utf-8'))
    clientSocket.close()

