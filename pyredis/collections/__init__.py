#!/usr/bin/env python
# coding: utf8

"""
    TO DOCUMENT
"""

from functools import partial
from typing import Callable, Union

from redis import Redis  # pylint: disable=import-error

from ..pool import RedisPool


class RedisCollection(object):
    """
        Base class for each implemented collection in this package.

        This class aims to proxy a `redis.Redis` client using a fixed
        collection name which will be used as collection key in Redis.

        Method from delegate client are proxyfied using internal name
        to provide easy access to Redis operation into collections :

        ```python
        class MyCollection(RedisCollection):
            def push_head(self, item):
                # self.lpush is mapped to Redis.lpush(key, item)
                # but proxyfication allow to not set key all the
                # time using functools.partial(operation, name).
                self.lpush(item)
        ```
    """

    def __init__(self, name: str, redis: Union[str, Redis] = None):
        """ Default constructor.

        Parameters
        ----------
        name: str
            Name of this list as Redis list name.
        redis: Union[str, redis.Redis]
            (Optional) a target redis client to use for operation proxying.
            Could be either a raw `redis.Redis` connection, or a string
            denoting a registered `redis.Redis` object from `pool.RedisPool`.
            Default is `None` which aims to use the default instance from
            `pool.RedisPool`.
        """
        self._name = name
        self._redis = RedisPool.get(redis)
        self._proxies = {}

    def __getattr__(self, key: str) -> Callable:
        """
        Parameters
        ----------
        key: str

        Returns
        -------
        operation: Callable

        Raises
        ------
        AttributeError
        """
        if key not in self._proxies:
            proxy = getattr(self._redis, key, None)
            if proxy is None:
                raise AttributeError(
                    "RedisCollection has no attribute '{}'".format(key))
            self._proxies[key] = partial(proxy, self._name)
        return self._proxies[key]
