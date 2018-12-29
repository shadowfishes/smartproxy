# -*- coding:utf-8 -*-
# 代理服务器脚本

import socket
import logging
import threading

import handler
from Pool import scheduler, dbop

logger = logging.getLogger("main.proxyserver")
# socket.setdefaulttimeout(2)


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

    def __init__(self, host="127.0.0.1", port=8899, max_conn=500, auto=False):
        super(Server, self).__init__()
        self.host = host
        self.port = port
        self.max_conn = max_conn
        self.socket = None
        self.auto = auto

    def run(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(self.max_conn)

            # 开始代理池功能
            if self.auto == "True":
                pool = threading.Thread(target=self.update_pool)
                pool.daemon = True
                pool.start()

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

        # 实现上级代理功能
        if self.auto == "True":
            logger.debug("启用上级代理功能")
            with dbop.DataOp(db_name="proxies", collection_name="foreign") as db:

                try:
                    res = db.get_best()
                    logger.debug("获取最优代理成功")
                    logger.debug("代理IP和端口为"+repr(res))
                    proxy.server = handler.Tcp2Server(res["ip"], int(res["port"]))
                    proxy.server.connect()
                    proxy.server.closed = False
                    logger.debug("上级代理设置成功")
                except Exception as err:
                    if proxy.server:
                        proxy.server.closed = True
                    logger.exception("上级代理设置失败，按正常代理进行处理"+repr(err))
        proxy.daemon = True
        logger.info(repr(addr))
        logger.debug('开始处理%s的请求' % repr(addr))
        proxy.start()

    def update_pool(self):
        scheduler.schedule_task("proxies", "foreign", 30)
