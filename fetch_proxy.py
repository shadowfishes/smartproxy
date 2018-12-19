#! *-* coding:utf-8 *-*

import requests
import random
import time
from bs4 import BeautifulSoup

usragent = ["Mozilla/5.0 (Windows NT 10.0; WOW64)", 'Mozilla/5.0 (Windows NT 6.3; WOW64)',
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


class IpInfo:
    __slots__ = ("ip", "port", "protocol", "dead")

    def __init__(self, ip=None, port=None, protocol=None, dead=0):
        self.ip = ip
        self.port = port
        self.protocol = protocol
        self.dead = dead


class GetProxy:
    def __init__(self):
        self.__savespider = dict()
        self.proxyresult = []

    def addspider(self, url):
        def wrapper(func):
            self.__savespider[url] = func
            return func
        return wrapper

    def runspider(self):
        for url, spider in self.__savespider.items():
            self.proxyresult.extend(spider(url))

    def showresult(self):
        for i in self.proxyresult:
            print(i.ip, i.port, i.protocol, i.dead, sep=":")

    def update(self, time_interval=0):
        pass

    def save2db(self):
        if not self.proxyresult:
            pass
        else:
            pass


myproxy = GetProxy()


@myproxy.addspider("http://www.xicidaili.com/wt/")
def getproxy_xici(url):
    httpproxy = []
    for page in range(1, 5):
        header = {"user-agent": random.choice(usragent)}
        pageurl = url + str(page)
        pagehtml = requests.get(pageurl, headers=header)
        pagecontent = pagehtml.text
        trs = BeautifulSoup(pagecontent, "html.parser").find_all("tr")
        for tr in trs[1:]:
            tds = tr.find_all("td")
            ip = tds[1].text.strip()
            port = tds[2].text.strip()
            protocol = tds[5].text.strip()
            httpproxy.append(IpInfo(ip, port, protocol))
        time.sleep(2)
    return httpproxy


@myproxy.addspider("https://www.kuaidaili.com/free/inha/")
def getproxy_kuaidaili(url):
    httpproxy = []
    for page in range(1, 5):
        header = {"user-agent": random.choice(usragent)}
        pageurl = url + str(page) + r'/'
        pagehtml = requests.get(pageurl, headers=header)
        pagecontent = pagehtml.text
        trs = BeautifulSoup(pagecontent, "html.parser").find_all("tr")
        for tr in trs[1:]:
            tds = tr.find_all("td")
            ip = tds[0].text.strip()
            port = tds[1].text.strip()
            protocol = tds[3].text.strip()
            httpproxy.append(IpInfo(ip, port, protocol))
        time.sleep(2)
    return httpproxy

@myproxy.addspider("http://www.89ip.cn/")
def getproxy_kuaidaili(url):
    httpproxy = []
    for page in range(1, 5):
        header = {"user-agent": random.choice(usragent)}
        pageurl = url + "index_{0}.html".format(page)
        pagehtml = requests.get(pageurl, headers=header)
        pagecontent = pagehtml.text
        trs = BeautifulSoup(pagecontent, "html.parser").find_all("tr")
        for tr in trs[1:]:
            tds = tr.find_all("td")
            ip = tds[0].text.strip()
            port = tds[1].text.strip()
            protocol = 'http'
            httpproxy.append(IpInfo(ip, port, protocol))
        time.sleep(2)
    return httpproxy

@myproxy.addspider("http://www.ip3366.net/?stype=1&page=")
def getproxy_kuaidaili(url):
    httpproxy = []
    for page in range(1, 5):
        header = {"user-agent": random.choice(usragent)}
        pageurl = url + str(page)
        pagehtml = requests.get(pageurl, headers=header)
        pagecontent = pagehtml.text
        trs = BeautifulSoup(pagecontent, "html.parser").find_all("tr")
        for tr in trs[1:]:
            tds = tr.find_all("td")
            ip = tds[0].text.strip()
            port = tds[1].text.strip()
            protocol = tds[3].text.strip()
            httpproxy.append(IpInfo(ip, port, protocol))
        time.sleep(2)
    return httpproxy


if __name__ == "__main__":
    print("testing")
    myproxy.runspider()
    myproxy.showresult()
