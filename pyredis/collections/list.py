#!/usr/bin/env python
# coding: utf8

""" TO DOCUMENT """

from collections.abc import Sequence
from typing import Any, Union

from . import RedisCollection


class RedisList(RedisCollection, Sequence):
    """
    """

    def __len__(self) -> int:
        """ `len()` operator overloading.

        Returns
        -------
        length: int
            List length as returned by `LLEN` operation.
        """
        self.llen()

    def __contains__(self, x) -> bool:
        """
        """
        pass

    def __add__(self, other: 'RedisList'):
        """
        """
        pass

    def __mul__(self, n: int) -> None:
        """
        """
        pass

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

    def __setitem__(self, key: int, value: Any) -> None:
        """
        Parameters
        ----------
        key; int
        value: Any
        """
        if not isinstance(key, int):
            raise KeyError('Only direct assignment is supported for RedisList')
        self.lset(key, value)

    def append(self, item: Any) -> None:
        """
        """
        self.lpush(item)

    def copy(self, name: str):
        """
        """
        
        pass

    def count(self, item: Any) -> int:
        """
        """
        values = self.lrange(0, len(self))
        values.count(item)

    def clear(self):
        """
        """
        for _ in range(len(self)):
            self.lpop()

    def extend(self, iterable):
        """
        """
        for item in iterable:
            self.append(item)

    def index(self, item: Any, i: int = 0, j: int = None) -> int:
        """
        """
        if j is None:
            j = len(self)
        values = self.lrange(i, j)
        # TODO: encode / decode check.
        return values.index(item, i, j)

    def insert(self, index: int, item: Any):
        """
        """
        pivot = self[index]
        self.linsert('BEFORE', pivot)

    def pop(self, index: int = None):
        """
        """
        if index is None:
            return self.rpop()
        if index == 0:
            return self.lpop()
        direction = 1
        if len(self) / 2 < index:
            direction = -1
        value = self[index]
        self.lset(index, '')
        self.lrem(direction, '')
        return value

    def remove(self, item: Any):
        """
        """
        if self.lrem(1, item) == 0:
            raise ValueError()

    def reverse(self):
        """
        """
        values = self.lrange(0, len(self))
        values.reverse()
        for value in values:
            self.rpush(value)
        self.ltrim(-1 * len(values), -1)

    def sort(self):
        """
        """
        values = self.lrange(0, len(self))
        values.sort()
        for value in values:
            self.rpush(value)
        self.ltrim(-1 * len(values), -1)
