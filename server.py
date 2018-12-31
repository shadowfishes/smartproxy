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

            # 开始代理池和数据库缓存功能
            if self.auto == "True":
                pool = threading.Thread(target=self.update_pool)
                pool.daemon = True
                pool.start()
                # 设置数据库缓存(5s有效期)，避免频繁读取
                self._cache = DbCache(5)
                # self._cache.set_cache()

            while True:
                logger.info("等待客户端连接")
                conn, addr = self.socket.accept()
                self.handler(conn, addr)
        except Exception as e:
            logger.exception(e)
        finally:
            self.socket.close()
            logger.info("关闭代理服务器")
            if hasattr(self, "_cache"):
                self._cache.close_cache()

    def handler(self, conn, addr):
        client = handler.Tcp2Client(conn, addr)
        proxy = handler.HTTPHandle(client)

        # 实现上级代理功能
        if self.auto == "True":
            logger.debug("启用上级代理功能")
            res = self._cache.get_cache()
            if not res:
                logger.exception("无法获取上级代理信息，按正常代理进行处理")
            else:
                try:
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


class DbCache:
    _lock = threading.Lock()

    # 单例模式，线程安全
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            with cls._lock:
                if not hasattr(cls, "_instance"):
                    cls._instance = object.__new__(cls)

        return cls._instance

    # 实例初始化，expired是缓存有效时间，单位sencond
    def __init__(self, expired):
        if not hasattr(self, "expired"):
            self.expired = expired
            self._cache = dict()

    def set_cache(self):
        # self.close_cache()
        timer = threading.Timer(self.expired, self.close_cache, [])
        self._cache["timer"] = timer
        self._cache["value"] = self.fetch_db()
        timer.start()

    def close_cache(self):
        if "timer" in self._cache:
            timer = self._cache.pop("timer")
            timer.cancel()
        if "value" in self._cache:
            self._cache.pop("value")

    def get_cache(self):
        if "value" not in self._cache:
            self.set_cache()
        return self._cache["value"]

    @staticmethod
    def fetch_db():
        with dbop.DataOp(db_name="proxies", collection_name="foreign") as db:
            try:
                res = db.get_best()
                logger.info("获取最优代理成功")
                logger.info("代理IP和端口为" + repr(res))
            except Exception as err:
                # logger.exception("获取代理失败，按正常代理进行处理：" + repr(err))
                return None
        return res
