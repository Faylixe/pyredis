#!/usr/bin/env python
# coding: utf8

"""
    This module provides a singleton responsible for managing Redis connection.

    Aims to be used for registering client from user perspective, and
    internally by `pyredis.collections` package for retrieving client.

    Examples
    --------
    ```python
    from pyredis.pool import RedisPool as pool
    from redis import Redis

    # Register Redis clients.
    pool.register(Redis(host='host1'), 'cache')
    pool.register(Redis(host='host2'), 'data', default=True)

    # Retrieve client.
    pool.default()
    pool.get('cache')
    ```
"""

from os import environ
from typing import Dict

from redis import Redis  # pylint: disable=import-error

DEFAULT_HOST = 'localhost'
""" Host for default fallback Redis instance. """

DEFAULT_PORT = 6379
""" Port for default fallback Redis instance. """


class RedisPool(object):
    """
        A RedisPool index redis.Redis client, managing default to be used for
        each collections.

        In case not client is registered, the pool will create a default client
        using `PYREDIS_HOST` and `PYREDIS_PORT` environment variables if
        available, or `DEFAULT_HOST` and `DEFAULT_PORT` module variables
        otherwise.
    """

    _default: Redis = None
    """ Default instance to be used. """

    _clients: Dict[str, Redis] = {}
    """ Indexed instances by name. """

    @classmethod
    def register(
            cls: type,
            redis: Redis,
            name: str = 'default',
            default: bool = False):
        """ Register the given Redis client to this pool under given name.

        Parameters
        ----------
        redis: redis.Redis
            Redis client instance to register.
        name: str
            (Optional) client associated name, used for indexing.
            Default to `default`.
        default: bool
            (Optional) indicate if given client should be used as default.
            Default to `False`

        Raises
        ------
        KeyError
            If a client is already registered with given name.
        """
        if name in cls._clients:
            raise KeyError(f'Redis client {name} is alreadt registered')
        if default:
            cls._default = redis
        cls._clients[name] = redis

    @classmethod
    def default(cls: type) -> Redis:
        """ Get default redis client, create it if not exists.

        Use `PYREDIS_HOST` and `PYREDIS_PORT` environment variables to
        determine how to connect to Redis, using `localhost:6379` as a
        default fallback.
        """
        if cls._default is None:
            host = environ.get('PYREDIS_HOST', DEFAULT_HOST)
            port = environ.get('PYREDIS_PORT', DEFAULT_PORT)
            cls._default = Redis(host=host, port=port)
        return cls._default

    @classmethod
    def get(cls: type, name: str = None) -> Redis:
        """ Retrieves a Redis client by `name` if possible.
        If no `name` is provided then it will fallback to `default()`.

        Parameters
        ----------
        name: str
            (Optional) name of the Redis client to retrieve, default to `None`.

        Returns
        -------
        client: redis.Redis
            Redis client required.

        Raises
        ------
        KeyError:
            If given `name` is not `None` and no client is found.
        """
        if name is None:
            return cls.default()
        if name not in cls._clients:
            raise KeyError(f'Redis client {name} not found')
        return cls._clients[name]
