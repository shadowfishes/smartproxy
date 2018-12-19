import socket
import threadpool
import urllib.parse
import select

BUFLEN = 4096


pool = threadpool.ThreadPool(10)

class Proxy:
    def __init__(self, conn, addr):
        super(Proxy, self).__init__()
        self.addr = addr
        self.source = conn
        self.request = ""
        self.headers = {}
        self.destnation = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.run()

    def get_headers(self):
        header = b''
        while True:
            tmprecv = self.source.recv(BUFLEN)
            if not tmprecv:
                header = header.decode()
                index = header.find('\n')
                break
            else:
                header += tmprecv

        # print("header:", header)
        # firstLine,self.request=header.split('\r\n',1)
        firstLine = header[:index]
        self.request = header[index + 1:]
        self.headers['method'], self.headers['path'], self.headers['protocol'] = firstLine.split()
        # print(self.headers)

    def conn_destnation(self):

        data = "%s %s %s\r\n" % (self.headers['method'], self.headers['path'], self.headers['protocol'])
        # print(data+self.request)

        url = urllib.parse.urlparse(self.headers['path'])
        hostname = url
        port = "80"
        print("here11111111111111111")
        if hostname.find(':') > 0:
            addr, port = hostname.split(':')
        else:
            addr = hostname
        port = int(port)
        print("here222222222222222222")
        ip = socket.gethostbyname(addr)
        print(ip, port)
        print("here33333333333333333")
        self.destnation.connect((ip, port))
        print("here44444444444444444")
        self.destnation.send(data + self.request)
        # print(data + self.request)

    def renderto(self):
        readsocket = [self.destnation]
        while True:
            data = ''
            (rlist, wlist, elist) = select.select(readsocket, [], [], 3)
            if rlist:
                data = rlist[0].recv(BUFLEN)
                if len(data) > 0:
                    self.source.send(data)
                else:
                    break
        # readsocket[0].close();

    def run(self):
        self.get_headers()
        self.conn_destnation()
        self.renderto()


class Server:

    def __init__(self, host, port, handler=Proxy):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(10)
        self.handler = handler

    def start(self):
        while True:
            try:
                # print("starting server:")
                # print(self.server)
                conn, addr = self.server.accept()
                print("reseive connect from:", addr)
                res = conn.recv(8192)
                print(res.decode())
                # t = self.handler(conn, addr)
                # t.start()
            except:
                pass


def test_server():
    raw_request = [b"CONNECT www.baidu.com:443 HTTP/1.1",
                   b"Host:www.baidu.com:443",
                   b"Proxy-Connection:keep-alive",
                   b"User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36(KHTML, likeGecko) Chrome/70.0.3538.110 Safari/537.36",
                   b"/r/n"
                   ]
    request = b"/r/n".join(raw_request)




test_sina()
if __name__ == '__main__':
    # s = Server("0.0.0.0", 8899)
    # s.start()
    pass