#!/usr/bin/env python
# coding: utf8

""" TO DOCUMENT """

from collections.abc import MutableSet
from typing import Any

from . import RedisCollection
from .. import markers


class RedisSet(RedisCollection, MutableSet):
    """
    """

    def __contains__(self, item: Any):
        """
        """
        return self.sismember(item)

    def __iter__(self):
        """
        """
        return self.sscan_iter()

    def __len__(self):
        """
        """
        return self.scard()

    def add(self, item: Any):
        """
        """
        self.sadd(item)

    def discard(self, item: Any):
        """
        """
        self.srem(item)

    def pop(self):
        """
        Returns
        -------
        """
        value = self.spop()
        if value is None:
            raise KeyError from None
        return value
