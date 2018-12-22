# -*- coding:utf-8 -*-

import requests
import datetime

from Pool.spider import SpiderMeta


class IpProxy:
    __slots__ = ["ip", "port", "protocol", "add_time", "last_verify_time", "success_counts",
                 "failed_counts", "delay"]

    def __init__(self, ip, port, protocol, add_time=None, success_counts=None, failed_counts=None,
                 delay=None):
        self.ip = ip
        self.port = port
        self.protocol = protocol
        self.add_time = add_time if add_time else datetime.datetime.utcnow()
        self.last_verify_time = self.add_time
        self.success_counts = success_counts if success_counts else 0
        self.failed_counts = failed_counts if failed_counts else 0
        self.delay = delay if delay else -1


class Verify:
    @classmethod
    def simple(cls):
        pass

    @classmethod
    def precise(cls):
        pass

