#!/usr/bin/env python
# coding: utf8

""" TO DOCUMENT """

from collections.abc import MutableSequence
from typing import Any, Union

from . import RedisCollection
from .. import markers


class RedisList(RedisCollection, MutableSequence):
    """
    """

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
