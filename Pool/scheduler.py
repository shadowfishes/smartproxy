# -*- coding:utf-8 -*-
# 代理池调度脚本，检测、添加、删除代理
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

from Pool import spider, verify, dbop


class Scheduler:

    def __init__(self, db_name="proxies", collection_name="foreign"):
        super(Scheduler, self).__init__()
        self.db = dbop.DataOp(db_name=db_name, collection_name=collection_name)
        self.raw_proxy = None
        self.proxies = None

    # 获取待检测的代理
    # 添加新代理，从爬虫获取； 检测已有代理，从数据库获取
    def get_proxy(self):
        raw_proxy = []
        if isinstance(self, AppendSched):
            for item in spider.SpiderMeta.get_proxy():
                raw_proxy.append(item)
        elif isinstance(self, VerifySched):
            raw_db = self.db.collectons.find()
            if raw_db is not None:
                for item in raw_db:
                    raw_proxy.append(item)
        self.raw_proxy = raw_proxy

    # 检测获取到的代理，最终得到可用代理集合
    def verify_proxy(self):
        vailed_proxy = []
        for res in verify.Verify.get_valid_proxy(self.raw_proxy, category=self.db.collection_name):
            if res:
                ip, port, protocol, theta_time = res
                vailed_proxy.append({"ip": ip, "port": port, "protocol": protocol, "delay": theta_time})
        self.proxies = vailed_proxy

    # 根据获取的可用代理，更新数据库
    def update_db(self):
        for item in self.proxies:
            index = {"ip": item["ip"], "port": item["port"]}
            # 数据已经存在，更新
            if self.db.collectons.find(index).count() != 0:
                self.db.collectons.update(index,
                                          {'$set': {"delay": item["delay"],
                                                    "last_verify_time": self.gettime()}})

            # 新增数据
            else:
                item["last_verify_time"] = self.gettime()
                self.db.collectons.insert(item)

    # 删除失效代理，判断依据为last_verify_time距今超过2小时。
    def delete_invalid_proxy(self):
        all_proxy = self.db.collectons.find()
        for proxy in all_proxy:
            now = self.gettime()
            delta = (self.convert_time(now) - self.convert_time(proxy["last_verify_time"]))
            if delta > datetime.timedelta(hours=2):
                self.db.collectons.remove(proxy)

    @staticmethod
    def gettime():
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    @staticmethod
    def convert_time(timestr):
        return datetime.datetime.strptime(timestr, "%Y-%m-%d %H:%M")

    def run(self):
        self.db.connect()
        self.get_proxy()
        self.verify_proxy()
        self.update_db()
        self.delete_invalid_proxy()
        self.db.close()


class AppendSched(Scheduler):
    def __init__(self, db_name, collection_name, time_interval):
        super(AppendSched, self).__init__(db_name, collection_name)
        self.time_interval = time_interval


class VerifySched(Scheduler):
    def __init__(self, db_name, collection_name, time_interval):
        super(VerifySched, self).__init__(db_name, collection_name)
        self.time_interval = time_interval


def schedule_task(db_name, collection_name, time_interval):

    # 定时任务
    task_append = AppendSched(db_name, collection_name, time_interval)
    task_verify = VerifySched(db_name, collection_name, time_interval/10)

    scheduler = BlockingScheduler()
    scheduler.add_job(func=task_append.run, trigger='interval', minutes=task_append.time_interval, id='add')
    scheduler.add_job(func=task_verify.run, trigger='interval', minutes=task_verify.time_interval, id='verify')
    scheduler.add_listener(my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    scheduler.start()


def my_listener(event):
    if event.exception:
        print('定时任务出错！')
    else:
        print('定时任务运行正常')


if __name__ == "__main__":
    # "proxies", "foreign" ：制定需要操作的数据库名和表名
    # 60 ：时间间隔单位为分钟
    schedule_task("proxies", "foreign", 30)
