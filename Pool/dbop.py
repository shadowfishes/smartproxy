# -*- coding:utf-8 -*-
# 数据库操作脚本【Mongodb】
# 可以根据需要进行修改

# import datetime
import pymongo
import pymongo.errors

#
# class IpProxy:
#     def __init__(self, ip, port, protocol, delay=None, last_verify_time=None, **kwargs):
#         self.ip = ip
#         self.port = port
#         self.protocol = protocol
#         self.last_verify_time = last_verify_time if last_verify_time else datetime.datetime.utcnow()
#         self.delay = delay if delay else -1
#
#     def change_to_dict(self):
#         res = dict()
#         for k, v in self.__dict__.items():
#             res[k] = v
#         return res
#
#     # 更新测试结果
#     def update(self, delay=0, success=True):
#         self.last_verify_time = datetime.datetime.utcnow()
#
#         # 计算平均时延，失败设置本次测试时延为10s
#         op_delay = delay if success else 10
#         self.delay = self.delay * (self.failed_counts + self.success_counts) + op_delay
#         self.delay = self.delay / (self.failed_counts + self.success_counts + 1)
#
#         if success:
#             self.success_counts += 1
#         else:
#             self.failed_counts += 1


class DataOp:
    def __init__(self, host="localhost", port=27017, db_name=None, collection_name=None):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.collection_name = collection_name
        self.conn = None
        self.db = None
        self.collectons = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def connect(self):
        try:
            conn = pymongo.MongoClient(self.host, self.port)
            conn.admin.command('ismaster')
        except pymongo.errors.ConnectionFailure:
            return None
        self.conn = conn
        self.db = self.conn[self.db_name]
        self.collectons = self.db[self.collection_name]
        return True

    def close(self):
        if self.conn:
            self.conn.close()
        self.conn = None
        self.db = None
        self.collectons = None

    def get_best(self):
        best = self.collectons.find()
        if best.count():
            return best.sort([("last_verify_time", -1), ("delay", 1)])[0]

    # 更新数据库，如果代理不存在，新增文档；存在则更新delay
    # datas： IpProxy组成的可迭代对象
    def update(self, datas):
        for data in datas:
            quote_res = self.collectons.find({"ip": data.ip, "port": data.port})
            if quote_res is None:
                self.collectons.insert(data.change_to_dict())
            else:
                self.collectons.update(
                    {"ip": data.ip, "port": data.port},
                    {'$set': {"delay": data.delay, "last_verify_time": data.last_verify_time}
                     }
                )

    # 删除数据
    def delete(self, data):
        self.collectons.remove({"ip": data.ip, "port": data.port})


if __name__ == "__main__":
    with DataOp(db_name="proxies", collection_name="foreign") as db:
        for i in db.collectons.find():
            print(i)
