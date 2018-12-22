# -*- coding:utf-8 -*-
import random
import logging
import time

import requests
from bs4 import BeautifulSoup

# 一些常用useragent
USRAGENT = ["Mozilla/5.0 (Windows NT 10.0; WOW64)", 'Mozilla/5.0 (Windows NT 6.3; WOW64)',
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
            'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36',
            'Mozilla/5.0 (Windows; U; Windows NT 5.2) Gecko/2008070208 Firefox/3.0.1',
            'Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070309 Firefox/2.0.0.3',
            'Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070803 Firefox/1.5.0.12',
            'Opera/9.27 (Windows NT 5.2; U; zh-cn)',
            'Mozilla/5.0 (Macintosh; PPC Mac OS X; U; en) Opera 8.0',
            'Opera/8.0 (Macintosh; PPC Mac OS X; U; en)',
            'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Win64; x64; Trident/4.0)',
            'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0 ', ]


# 爬虫元类
class SpiderMeta(type):
    _spiders = []

    def __new__(cls, *args, **kwargs):
        if "getter" not in args[2]:
            raise NotImplementedError("爬虫类{0}的getter方法未实现".format(args[0]))

        # 为爬虫类添加获取页面表格方法
        args[2]["get_page"] = lambda url: SpiderMeta.get_page(url)

        cls._spiders.append(type.__new__(cls, *args, **kwargs))
        return type.__new__(cls, *args, **kwargs)

    @classmethod
    def get_proxy(cls):
        for spider in cls._spiders:
            yield from spider.getter()

    @staticmethod
    def get_page(url):
        # 随机选取agent，也可以不使用
        header = {"user-agent": random.choice(USRAGENT)}
        try:
            page = requests.get(url, headers=header)
            trs = BeautifulSoup(page.text, "html.parser").find_all("tr")
        except Exception:
            logging.exception("获取/解析页面{0}失败".format(url))
            return None
        return trs


# 自定义添加爬虫类，必须实现getter方法
class XiciSpider(metaclass=SpiderMeta):
    url = "http://www.xicidaili.com/wt/"

    # 以生成器的方式返回（IP，Port，Protocol）元组
    @classmethod
    def getter(cls):
        for page in range(1, 5):
            url = cls.url + str(page)
            trs = cls.get_page(url)
            if trs is None:
                continue
            for tr in trs[1:]:
                tds = tr.find_all("td")
                ip = tds[1].text.strip()
                port = tds[2].text.strip()
                protocol = tds[5].text.strip()
                yield (ip, port, protocol)
            time.sleep(1)


class KuaiSpider(metaclass=SpiderMeta):
    url = "https://www.kuaidaili.com/free/inha/"

    @classmethod
    def getter(cls):
        for page in range(1, 5):
            url = cls.url + str(page) + r'/'
            trs = cls.get_page(url)
            if trs is None:
                continue
            for tr in trs[1:]:
                tds = tr.find_all("td")
                ip = tds[0].text.strip()
                port = tds[1].text.strip()
                protocol = tds[3].text.strip()
                yield (ip, port, protocol)
            time.sleep(1)


class Mianfei89(metaclass=SpiderMeta):
    url = "http://www.89ip.cn/index_"

    @classmethod
    def getter(cls):
        for page in range(1, 5):
            url = cls.url + str(page) + r'.html'
            trs = cls.get_page(url)
            if trs is None:
                continue
            for tr in trs[1:]:
                tds = tr.find_all("td")
                ip = tds[0].text.strip()
                port = tds[1].text.strip()
                protocol = "HTTP"
                yield (ip, port, protocol)
            time.sleep(1)


class Ip3366(metaclass=SpiderMeta):
    url = "http://www.ip3366.net/?stype=1&page="

    @classmethod
    def getter(cls):
        for page in range(1, 5):

            url = cls.url + str(page)
            trs = cls.get_page(url)
            if trs is None:
                continue
            for tr in trs[1:]:
                tds = tr.find_all("td")
                ip = tds[0].text.strip()
                port = tds[1].text.strip()
                protocol = tds[3].text.strip()
                yield (ip, port, protocol)
            time.sleep(1)


if __name__ == "__main__":
    gen = SpiderMeta.get_proxy()
    counts = 0
    for proxy in gen:
        counts += 1
        print(proxy)
    print(counts)
