import json
import random
from functools import wraps

import redis

from conf.settings import backend_settings


def get_redis_client():
    return redis.StrictRedis(
        host=backend_settings.redis_host,
        port=backend_settings.redis_port,
        password=backend_settings.redis_passwd,
        ssl=True,
    )


redis_client = get_redis_client()


class RedisLock:
    """
    redis分布式锁的简单封装
    """

    def __init__(self, rnd=True):
        """
        rnd:是否使用随机数保证超时的函数并发安全
        """
        self.redis_client = redis_client
        self.tag = None
        self.rnd = rnd

    def set_lock(self, lock_name, ex=5) -> bool:
        """
        加锁
        参数：
            lock_name:锁名
            ex:超时时间，单位秒
        返回：true 加锁成功 false加锁失败,
        """
        # 生成随机数保证在超时情况下，只释放自己的锁
        self.tag = str(random.randint(1, 99999))
        return bool(self.redis_client.set(lock_name, self.tag, ex, nx=True))

    def del_lock(self, lock_name):
        """
        删除锁
        """
        tag = self.redis_client.get(lock_name)
        if self.rnd and tag != self.tag:
            return
        self.redis_client.delete(lock_name)


redis_lock = RedisLock()

cache = redis_client


def cache_function(expiry: int = 30):
    cache_function_pattern = (
        "cache_function_{func_module}_{func_name}_{args}_{varargs}_{kwargs}"
    )

    def inner_function(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = get_cache_key(func, *args, **kwargs)

            if cache_key:
                cached_data = cache.get(cache_key)
                if cached_data:
                    try:
                        data = json.loads(cached_data)
                    except Exception:
                        data = cached_data
                    return data

            data = func(*args, **kwargs)

            if cache_key:
                if isinstance(data, str):
                    cache.set(cache_key, data, ex=expiry)
                else:
                    cache.set(cache_key, json.dumps(data), ex=expiry)
            return data

        return wrapper

    def get_cache_key(func, *args, **kwargs):
        args_map, varargs, kwargs = validate_get_arguments(func, *args, **kwargs)

        if args_map is None or varargs is None or kwargs is None:
            return None

        return cache_function_pattern.format(
            func_module=func.__module__,
            func_name=func.__name__,
            args=str(args_map),
            varargs=str(varargs),
            kwargs=str(kwargs),
        )

    def validate_get_arguments(func, *varargs, **kwargs):
        varargs = list(varargs)
        kwargs = kwargs.copy()
        code = func.__code__

        args_names = code.co_varnames[: code.co_argcount]
        args_map = {}

        args_names_extra = (
            args_names[len(varargs) :] if len(args_names) > len(varargs) else []
        )

        args_names = args_names[: len(varargs)]

        if any([args_name in kwargs for args_name in args_names]):
            return None, None, None
        for i in range(len(args_names)):
            args_map[args_names[i]] = varargs[i]

        varargs = varargs[len(args_names) :]

        if any([args_name not in kwargs for args_name in args_names_extra]):
            return None, None, None
        for args_name in args_names_extra:
            args_map[args_name] = kwargs.pop(args_name)

        return args_map, varargs, kwargs

    return inner_function
