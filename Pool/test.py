import threading
import uuid
import time

value_list = ["first", "second", "third", "fourth", "fifth"]


# 具有时效性的缓存设计
class ProxyCache:
    _Lock = threading.Lock()
    # 默认缓存时限
    EXPIRED = 60

    # 单例模式
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_single"):
            with cls._Lock:
                if not hasattr(cls, "_single"):
                    cls._single = object.__new__(cls)
        return cls._single

    def __init__(self, expired=None):
        # 避免重置缓存
        self.expired = expired if expired else ProxyCache.EXPIRED
        self._id = None
        if not hasattr(self, "_cache"):
            self._cache = dict()

    def set_cache(self, cache_id=None, value=None):
        if not cache_id:
            cache_id = uuid.uuid1()
        self._id = cache_id
        self._set_cache(cache_id, value)
        return cache_id

    def _set_cache(self, cache_id, value):
        self.stop_cache(cache_id)
        timer = threading.Timer(self.expired, self.stop_cache, [cache_id])
        timer.start()
        self._cache[cache_id] = {"value": value, "timer": timer}

    def stop_cache(self, cache_id):
        if cache_id in self._cache:
            timer = self._cache[cache_id]["timer"]
            value = self._cache[cache_id]["value"]
            timer.cancel()
            self._cache.pop(cache_id)
            index = (value_list.index(value) + 1) % len(value_list)
            self.set_cache(value=value_list[index])

    def get_cache(self, cache_id):
        if cache_id in self._cache:
            return self._cache[cache_id]["value"]
        else:
            return None


if __name__ == "__main__":
    cache = ProxyCache(3)
    cache_id = cache.set_cache(value="first")
    for i in range(100):
        print(cache.get_cache(cache._id))
        time.sleep(1)
