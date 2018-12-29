# -*- coding:utf-8 -*-
# 代理验证脚本

import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# 多线程总数
import os
MAX_THREAD = os.cpu_count() * 10


class Verify:

    # 测试地址， 分国内和国外
    local_url = "http://www.baidu.com"
    foreign_url = "http://www.google.com"

    # proxies: 未测试的代理集合，(ip, port, protocol)三元组或者字典构成的可迭代对象
    # 返回值： 有效的代理，(ip, port, protocol，delay)四元组构成的生成器
    @classmethod
    def get_valid_proxy(cls, proxies, category="local"):
        if category == "local":
            func = Verify.simple
        elif category == "foreign":
            func = Verify.precise
        else:
            raise ValueError("错误的代理类型参数: local 或者 foreign")
        with ThreadPoolExecutor(max_workers=MAX_THREAD) as executor:
            futures = [executor.submit(func, **proxy) if isinstance(proxy, dict) else executor.submit(func, *proxy)
                       for proxy in proxies]
            for res in as_completed(futures):
                if res.result():
                    yield res.result()

    # 这里可以自定义检测国内代理方法
    @classmethod
    def simple(cls, ip, port, protocol, **kwargs):
        proxies = {protocol.lower(): r"{0}://{1}:{2}".format(protocol.lower()[:4], ip, port)}
        try:
            last = time.time()
            response = requests.get(cls.local_url, proxies=proxies, timeout=2)
            theta_time = time.time() - last
            if response.status_code == 200 and "百度一下，你就知道".encode() in response.content:
                return ip, port, protocol, theta_time
        except Exception as err:
            return None

    # 这里可以自定义检测国外代理方法
    @classmethod
    def precise(cls, ip, port, protocol, **kwargs):
        proxies = {protocol.lower(): r"{0}://{1}:{2}".format(protocol.lower()[:4], ip, port)}
        try:
            last = time.time()
            response = requests.get(cls.foreign_url, proxies=proxies, timeout=2)
            theta_time = time.time() - last
            if response.status_code == 200 and r"<title>Google</title>" in response.text:
                return ip, port, protocol, theta_time
        except Exception:
            return None


if __name__ == "__main__":
    # 使用示例
    from Pool.spider import SpiderMeta

    # 获取未测试的代理地址（获得生成器）
    un_proxies = SpiderMeta.get_proxy()
    local_proxies = Verify.get_valid_proxy(un_proxies)

    print("以下是国内代理测试结果：")
    for result in local_proxies:
        if result:
            print(result)

    # 由于未测试的代理集合为生成器，需要重新获取
    un_proxies = SpiderMeta.get_proxy()
    foreign_proxies = Verify.get_valid_proxy(un_proxies, category="foreign")

    print("以下是国外代理测试结果：")
    for result in foreign_proxies:
        if result:
            print(result)
