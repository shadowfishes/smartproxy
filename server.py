# -*- coding:utf-8 -*-

import socket
import logging
import threading

import handler

logger = logging.getLogger("main.proxyserver")


class Server:
    """
    代理服务器类，多线程处理客户端发来的socket请求
    """

    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        """
        单例模式,线程安全,只允许创建一个server实例
        """
        if not hasattr(cls, "__instance"):
            with cls._instance_lock:
                if not hasattr(cls, "__instance"):
                    cls.__instance = object.__new__(cls)
        else:
            logger.critical("同时只允许一个服务器实例运行")
            raise RuntimeError("同时只允许一个服务器实例运行")
        return cls.__instance

    def __init__(self, host="127.0.0.1", port=8899, max_conn=500):
        super(Server, self).__init__()
        self.host = host
        self.port = port
        self.max_conn = max_conn
        self.socket = None

    def run(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(self.max_conn)
            while True:
                logger.info("等待客户端连接")
                conn, addr = self.socket.accept()
                self.handler(conn, addr)
        except Exception as e:
            logger.exception(e)
        finally:
            self.socket.close()
            logger.info("关闭代理服务器")

    def handler(self, conn, addr):
        client = handler.Tcp2Client(conn, addr)
        proxy = handler.HTTPHandle(client)
        proxy.daemon = True
        logger.debug('开始处理%r的请求' % client)
        proxy.start()
