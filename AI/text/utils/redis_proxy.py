import redis
from .connection_manager import connection_manager

class RedisProxy:
    def __init__(self, client, name):
        self._client = client
        self._name = name
        
    def __getattr__(self, item):
        original_attr = getattr(self._client, item)
        if callable(original_attr):
            def wrapper(*args, **kwargs):
                connection_manager.ensure_connection(self._name, self._client.ping)
                try:
                    result = original_attr(*args, **kwargs)
                    connection_manager.set_status(self._name, 'connected')
                    return result
                except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError, ConnectionResetError) as e:
                    connection_manager.set_status(self._name, 'disconnected')
                    raise e
            return wrapper
        return original_attr
