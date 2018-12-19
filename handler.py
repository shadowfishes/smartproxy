# -*- coding:utf-8 -*-

import select
import datetime
import threading
import logging
import socket
import errno

from parse import *

logger = logging.getLogger("main.httphandle")


class BaseTcpConnect:
    """
    基本的socket TCP连接， 带缓存。
    """
    def __init__(self, conn_to):
        self.buffer = b""
        self.conn = None
        self.closed = False
        self.conn_to = conn_to

    def recv(self, length=RECV_MAX_LENGTH):
        try:
            data = self.conn.recv(length)
            if len(data) == 0:
                logger.debug('从 %s 收到 0 字节数据' % self.conn_to)
                return None
            logger.debug('从 %s 收到 %d 字节数据' % (self.conn_to, len(data)))
            return data
        except Exception as err:
            if err.errno == errno.ECONNRESET:
                logger.debug('%r' % err)
            else:
                logger.exception(
                    '从%s接受数据时发生错误， 错误原因：%r' % (self.conn_to, err))
            return None

    def send(self, data):
        return self.conn.send(data)

    def flush(self):
        count = self.send(self.buffer)
        self.buffer = self.buffer[count:]
        logger.debug('向 %s 写入 %d 字节的数据' % (self.conn_to, count))

    def close(self):
        self.conn.close()
        self.closed = True

    def has_buffer(self):
        return len(self.buffer) > 0

    def add2buffer(self, data):
        self.buffer += data

    def clearbuffer(self):
        self.buffer = b''


class Tcp2Client(BaseTcpConnect):
    """
    连接代理用户的socket连接
    """
    def __init__(self, conn, addr):
        super(Tcp2Client, self).__init__(b"client")
        self.conn = conn
        self.addr = addr


class Tcp2Server(BaseTcpConnect):
    """
    连接目标服务器的socket连接
    """
    def __init__(self, host, port):
        super(Tcp2Server, self).__init__(b"server")
        self.addr = (host, int(port))

    def connect(self):
        self.conn = socket.create_connection(self.addr)


class HTTPHandle(threading.Thread):
    def __init__(self, client):
        super(HTTPHandle, self).__init__()

        self.client = client
        self.server = None

        self.start_time = self._gettimenow()
        self.last_active = self._gettimenow()

        self.request = RequestParse()
        # self.response = ResponseParse()

        self.proxy_established = SEP_LINE.join([
            b'HTTP/1.1 200 Connection established',
            b'Proxy-agent: httpproxy ',
            SEP_LINE
        ])

    @staticmethod
    def _gettimenow():
        return datetime.datetime.utcnow()

    def _inactive_time(self):
        return (self.last_active - self.start_time).seconds

    def _is_inactive(self):
        return self._inactive_time() > 30

    def get_ready_con(self):
        readlist, writelist, errlist = [self.client.conn], [], []

        if self.client.has_buffer():
            writelist.append(self.client.conn)
            logger.debug("客户端缓存有数据，查询是否可写")

        if self.server and not self.server.closed:
            readlist.append(self.server.conn)
            logger.debug("已经建立到服务器的连接， 查询是否有数据可读")

        if self.server and not self.server.closed and self.server.has_buffer():
            writelist.append(self.server.conn)
            logger.debug("服务器缓存有数据，查询是否可写")

        return readlist, writelist, errlist

    def process_request(self, data):

        # 已将建立目标服务连接，直接转发客户端的请求数据
        if self.server and not self.server.closed:
            self.server.add2buffer(data)
            return

        # 解析客户端request数据，这里请求可能接受不完整
        self.request.parse(data)

        if self.request.state == REQUEST_PARSER_STATE_COMPLETE:
            logger.info("客户端请求解析完毕")
            host, port = None, None
            if self.request.method == b"CONNECT":
                host, port = self.request.urls.path.split(COLON)
            elif self.request.urls:
                host, port = self.request.urls.hostname, self.request.urls.port if self.request.urls.port else 80
            else:
                #  错误的请求
                pass
            self.server = Tcp2Server(host, port)
            try:
                logger.debug("尝试连接服务器")
                self.server.connect()
                logger.debug("已经连接到服务器")
            except Exception as e:
                logger.exception(e)
                self.server.closed = True
                raise Exception("连接服务器出错",host, port)

            if self.request.method == b"CONNECT":
                self.client.add2buffer(self.proxy_established)
            else:
                self.server.add2buffer(self.request.rebuild_request(
                    del_headers=[b'proxy-connection', b'connection', b'keep-alive'],
                    add_headers=[(b'Connection', b'Close')]))

    def process_response(self, data):
        # 直接转发，不解析
        self.client.add2buffer(data)

    def process_write(self, wl):
        if self.client.conn in wl:
            self.client.flush()
            logger.debug("向客户端写入缓存数据")

        if self.server and not self.server.closed and self.server.conn in wl:
            self.server.flush()
            logger.debug("向服务器端写入缓存数据")

    def process_read(self, rl):
        if self.client.conn in rl:
            logger.debug("客户端开始接收数据")
            data = self.client.recv()
            self.last_active = self._gettimenow()

            if not data:
                logger.debug("客户端关闭连接")
                return False

            try:
                self.process_request(data)
            except Exception as e:
                logger.exception(e)
                self.client.clearbuffer()
                self.client.add2buffer(SEP_LINE.join([
                    b'HTTP/1.1 502 Bad Gateway',
                    b'Proxy-agent: myproxy',
                    b'Content-Length: 11',
                    b'Connection: close',
                    SEP_LINE
                ]) + b'Bad Gateway')
                self.client.flush()
                return False

        if self.server and not self.server.closed and self.server.conn in rl:
            data = self.server.recv()
            logger.debug("服务器端开始接收数据")
            self.last_active = self._gettimenow()

            if not data:
                logger.debug('服务器端关闭连接')
                self.server.close()
            else:
                self.process_response(data)
        return True

    def working(self):
        while True:
            readlist, writelist, errlist = self.get_ready_con()
            rl, wl, el = select.select(readlist, writelist, errlist, 1)

            self.process_write(wl)

            # 发生错误或者客户端关闭连接，终止本次代理运行
            if not self.process_read(rl):
                break

            if not self.client.has_buffer:
                if self._is_inactive():
                    logger.debug("客户端空闲超时，终止本次连接")
                    break
                # if self.response.state == HTTP_PARSER_STATE_COMPLETE:
                #     logger.debug("本次代理完成，退出")
                #     break

    def run(self):
        logger.debug('收到连接请求： %r at address %r' % (self.client.conn, self.client.addr))
        try:
            self.working()
        except Exception as err:
            logger.debug(" 发生错误，错误为：%r", err)
        finally:
            if self.server and (not self.server.closed):
                self.server.close()
            logger.debug('关闭连接： %r at address %r' % (self.client.conn, self.client.addr))




print()