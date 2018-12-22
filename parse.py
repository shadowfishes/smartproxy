# -*- coding:utf-8 -*-
import logging
import urllib.parse

logger = logging.getLogger("main.httpparse")


RECV_MAX_LENGTH = 8192
SEP_LINE, COLON, SPACE = b'\r\n', b':', b' '

# Request状态标志
REQUEST_PARSER_STATE_START = 1
REQUEST_PARSER_STATE_LINE_RECVD = 2
REQUEST_PARSER_STATE_HEARDER_RECV = 3
REQUEST_PARSER_STATE_HEARDER_COMPLETE = 4
REQUEST_PARSER_STATE_BODY_RECV = 5
REQUEST_PARSER_STATE_COMPLETE = 6

# Response状态标志
RESPONSE_PARSER_STATE_START = 1
RESPONSE_PARSER_STATE_LINE_RECVD = 2
RESPONSE_PARSER_STATE_HEARDER_RECV = 3
RESPONSE_PARSER_STATE_HEARDER_COMPLETE = 4
RESPONSE_PARSER_STATE_BODY_RECV = 5
RESPONSE_PARSER_STATE_COMPLETE = 6


class Parser:
    def __init__(self):
        self.state = REQUEST_PARSER_STATE_START
        self.raw = b""
        self.buffer = b''

        self.method = None
        self.urls = None
        # self.hostname = None
        self.headers = dict()
        self.body = None
        self.trunk = None

        self.version = None

    def parse(self, data):
        self.raw += data
        data += self.buffer
        self.buffer = b''
        notdone = len(data)
        while notdone:
            notdone, data = self.process(data)
        self.buffer = data

    def rebuild_url(self):
        if not self.urls:
            return b'/None'

        url = self.urls.path
        if url == b'':
            url = b'/'
        if not self.urls.query == b'':
            url += b'?' + self.urls.query
        if not self.urls.fragment == b'':
            url += b'#' + self.urls.fragment
        return url

    def process(self, data):
        raise NotImplementedError()

    @staticmethod
    def line_split(data):
        index = data.find(SEP_LINE)
        if index == -1:
            return False, data
        else:
            line = data[:index]
            data = data[index+len(SEP_LINE):]
            return line, data

    @staticmethod
    def build_header(key, value):
        return key + b': ' + value + SEP_LINE


class RequestParse(Parser):
    def process(self, data):
        if self.state >= REQUEST_PARSER_STATE_HEARDER_COMPLETE:
            if self.method == "POST":
                if not self.body:
                    self.body = b""
                if b'content-length' in self.headers:
                    self.state == REQUEST_PARSER_STATE_BODY_RECV
                    self.body += data
                    if len(self.body) >= int(self.headers[b'content-length']):
                        self.state = REQUEST_PARSER_STATE_COMPLETE
            return False, b""
        else:
            line, data = Parser.line_split(data)
            if line is False:
                return False, data

            if self.state < REQUEST_PARSER_STATE_LINE_RECVD:
                self.method, self.urls, self.version = line.split(SPACE, maxsplit=2)
                self.method = self.method.upper()
                self.urls = urllib.parse.urlparse(self.urls)
                self.state = REQUEST_PARSER_STATE_LINE_RECVD
            else:
                if len(line) == 0:
                    if self.state == REQUEST_PARSER_STATE_HEARDER_RECV:
                        self.state = REQUEST_PARSER_STATE_HEARDER_COMPLETE
                    elif self.state == REQUEST_PARSER_STATE_LINE_RECVD:
                        self.state = REQUEST_PARSER_STATE_HEARDER_RECV
                else:
                    self.state = REQUEST_PARSER_STATE_HEARDER_RECV
                    key, value = line.split(COLON, maxsplit=1)
                    self.headers[key.strip().lower()] = value.strip()
            if self.state == REQUEST_PARSER_STATE_HEARDER_COMPLETE and not self.method == b'POST' \
                    and self.raw.endswith(SEP_LINE * 2):
                self.state = REQUEST_PARSER_STATE_COMPLETE
            return len(data), data

    def rebuild_request(self, del_headers=None, add_headers=None):
        req = SPACE.join([self.method, self.rebuild_url(), self.version])
        req += SEP_LINE
        del_header = del_headers if del_headers else []
        add_header = add_headers if add_headers else []
        for k in self.headers:
            if k not in del_header:
                req += self.build_header(k, self.headers[k])
        for k in add_header:
            req += self.build_header(k[0], k[1])
        req += SEP_LINE
        if self.body:
            req += self.body
        return req























