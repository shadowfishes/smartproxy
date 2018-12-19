 # coding:utf-8
from socket import *
import requests

# 创建socket，绑定到端口，开始监听
tcpSerPort = 8899
tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

# Prepare a server socket
tcpSerSock.bind(('127.0.0.1', tcpSerPort))
tcpSerSock.listen(1)

while True:
    # 开始从客户端接收请求
    print('Ready to serve...')
    tcpCliSock, addr = tcpSerSock.accept()
    print('Received a connection from: ', addr)
    message = tcpCliSock.recv(4096).decode()
    print(message)
    tcpCliSock.close()

