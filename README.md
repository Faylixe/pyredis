# pyredis

Pythonic Redis backed data structure



## Managing connection.

```python
from redis import Redis

import pyredis

# Create a custom redis client first.
redis = Redis(...)
# Setup as default connection.
pyredis.register(redis)
# Setup as named connection.
pyredis.register(redis, 'connection1')
```

## Use datastructure

```python
from pyredis.collections import List as rlist

# Create a Redis backed list.
l = rlist('mylist')
# lpush('mylist', 'My item')
l.append('My item')
# llen('mylist')
print(len(l))
```