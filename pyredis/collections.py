#!/usr/bin/env python
# coding: utf8

"""
    TO DOCUMENT
"""

from collections.abc import MutableMapping, MutableSequence, MutableSet
from functools import partial
from typing import Any, Callable, Union
from uuid import uuid4

from redis import Redis  # pylint: disable=import-error

from . import markers
from .pool import RedisPool


class RedisCollection(object):
    """ Base class for each implemented collection in this package.

    This class aims to proxy a `redis.Redis` client using a fixed
    collection name which will be used as collection key in Redis.

    Method from delegate client are proxyfied using internal name
    to provide easy access to Redis operation into collections :

    Examples
    --------
    `self.lpush` is mapped to `Redis.lpush(key, item)` but
    proxyfication allow to not set key all the time using
    `functools.partial(operation, name)` :

    >>> class MyCollection(RedisCollection):
    ...     def push_head(self, item):
    ...         self.lpush(item)
    """
    def __init__(self, name: str = None, redis: Union[str, Redis] = None):
        """ Default constructor.

        Parameters
        ----------
        name: str
            (Optional) name of this list as Redis list name, if not provided
            an anonymous name will be generated and stored into
            `pyredis:anonymous` set. Default is `None`.
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
        if self._name is None:
            name = uuid4().hex
            self._name = f'{markers.anonymous}:{name}'
            self._redis.sadd(markers.anonymous, name)

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


class RedisSet(RedisCollection, MutableSet):
    """ A MutableSet implementation backed by a Redis set.

    Examples
     --------
    >>> from pyredis.collections import RedisSet as rset

    Using anonymous set

    >>> s = rset()
    >>> s.add('one')
    >>> s.add('two')
    >>> s.add('three')
    >>> for item in s:
    ...     print(s)
    one
    two
    three

    Using named set

    >>> ns = rset('myset')
    >>> ns.add('persistant')
    >>> print(len(ns))
    1
    """

    def __init__(
            self,
            name: str = None,
            redis: Union[str, Redis] = None):
        """
        """
        super().__init__(name, redis)

    def __contains__(self, item: Any) -> bool:
        """ Check if the given item is present into this set.

        Parameters
        ----------
        item: Any
            Item to search for.

        Returns
        -------
        present: bool
            `True` if `item` is within this set, `False` otherwise.

        Notes
        -----
        This method use `SISMEMBER` operation and thus run in _O(1)_ time
        complexity.
        """
        return self.sismember(item)

    def __iter__(self):
        """ Create an iterator for this set's values.

        Returns
        -------
        iterator: Iterator
            Set value iterator.

        Notes
        -----
        This method use `SSCAN` operation through `Redis.sscan_iter` utility
        and thus run in _O(N)_ time complexity, where _N_ is the number of
        element in this set.
        """
        return self.sscan_iter()

    def __len__(self) -> int:
        """ Return the size of this set.

        Returns
        -------
        length: int
            Size of this set.

        Notes
        -----
        This method use to `SCARD` operation and thus run in _O(1)_ time
        complexity.
        """
        return self.scard()

    def add(self, item: Any):
        """
        Parameters
        ----------
        item: Any
            Item to be added in this set.

        Notes
        -----
        This method use `SADD` operation and thus run in _O(1)_ time
        complexity.
        """
        self.sadd(item)

    def discard(self, item: Any):
        """ Remove the given item from this set

        Parameters
        ----------
        item: Any
            Item to be removed from this set.
        """
        self.srem(item)

    def pop(self):
        """ Pop a random element from this set.

        Returns
        -------
        item: Any
            Item poped.

        Raises
        ------
        KeyError
            If the set is empty.

        Notes
        -----
        This method use `SPOP` operation and thus run in _O(1)_ time
        complexity.
        """
        value = self.spop()
        if value is None:
            raise KeyError from None
        return value


class RedisList(RedisCollection, MutableSequence):
    """ A MutableSequence implementation backed by a Redis list.

    Examples
    --------
    >>> from pyredis.collections import RedisList as rlist

    Using anonymous list

    >>> l = rlist([1, 2, 3])
    >>> l.append(4)
    >>> for x in l:
    ...     print(x)
    1
    2
    3

    Using named list

    >>> l = rlist('mylist')
    >>> print(len(l))
    0
    """
    def __init__(
            self,
            name: str = None,
            redis: Union[str, Redis] = None):
        """
        """
        super().__init__(name, redis)

    def _remove(
            self,
            indexes: slice,
            length: int):
        """
        Parameters
        ----------
        indexes: slice
        length: int
        """
        start, stop, step = indexes.indices(length)
        if start > stop:
            start, stop = stop, start
        # Note: rotate last N element back.
        for _ in range(stop, length):
            self.rpoplpush(self._name)
        # Note: remove item in range.
        for _ in range(start):
            # TODO: handle step here.
            self.rpop()
        # Note: rotate first N element back.
        for _ in range(start + 1):
            self.rpoplpush(self._name)

    def __delitem__(self, key: Union[int, slice]):
        """
        Notes
        -----
        O(N) complexity.
        """
        length = len(self)
        if isinstance(key, int):
            # Note: for absolute index in head or tail we can achieve
            #       O(1) by using [l|r]push().
            if abs(key) < 0 or abs(key) >= length:
                raise IndexError('RedisList index ouf of range')
            if key == 0 or key == -1 * length:
                self.lpop()
            elif key == length or key == -1:
                self.rpop()
            else:
                self._remove(slice(key, key), length)
        elif isinstance(key, slice):
            self._remove(key, length)
        else:
            raise KeyError(
                'Only int or slice indexing is supported for RedisList')

    def __getitem__(self, key: Union[int, slice]) -> Any:
        """
        Parameters
        ----------
        key: Union[int, slice]

        Returns
        -------
        value: Any
        """
        if isinstance(key, int):
            return self.lindex(key)
        if isinstance(key, slice):
            return self.lrange(key.start, key.stop)[key]
        raise KeyError('Only int or slice indexing is supported for RedisList')

    def __len__(self) -> int:
        """ `len()` operator overloading.

        Returns
        -------
        length: int
            List length as returned by `LLEN` operation.
        """
        self.llen()

    def __setitem__(self, key: int, value: Any) -> None:
        """
        Parameters
        ----------
        key: int
        value: Any
        """
        if not isinstance(key, int):
            raise KeyError('Only direct assignment is supported for RedisList')
        self.lset(key, value)

    def insert(self, index: int, item: Any):
        """
        Parameters
        ----------
        index: int
        item: Any
        """
        if index == 0:
            self.lpush(item)
        elif index == len(self):
            self.rpush(item)
        else:
            pivot = self[index]
            self[index] = markers.insert
            self.linsert('BEFORE', markers.insert)
            self[index + 1] = pivot
