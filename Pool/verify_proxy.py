#! *-* coding:utf-8 *-*

import requests
import re
# import threading
# import queue
from bs4 import BeautifulSoup

VERIFYURL = ["www.google.com"]


def verifyip():
    result = None
    while 1:
        ip = yield result
        proxy = {ip.protocol.lower(): ip.ip + ":" + ip.port}
        # print(proxy)
        try:
            headers = {'Connection': 'close'}
            page = requests.get("http://www.google.com/ncr", proxies=proxy, headers=headers, timeout=10)
            result = True if "<title>Google</title>" in page.text else False
            if result:
                try:
                    with open("./html/" + ip.ip + "@" + ip.port + ".html", 'w+') as fp:
                        fp.write(page.text)
                except Exception as err:
                    print(err)
                finally:
                    if fp:
                        fp.close()
        except requests.RequestException as err:
            result = False
            print(err)
            continue


def getip(ips):
    ipresult = []
    verifygen = verifyip()
    verifygen.send(None)
    for ip in ips:
        result = verifygen.send(ip)
        if result:
            print("测试成功@", ip.ip)
            ipresult.append(ip)
    verifygen.close()
    return ipresult


