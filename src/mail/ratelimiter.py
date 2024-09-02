import time
from typing import List, Tuple


class RateLimiter:
    DB_PREFIX = 'rl'

    def __init__(self, redis_conn, limits: List[Tuple[int, int]], user_id: str = 'global'):
        self.redis = redis_conn
        self.limits = limits
        self.user_id = user_id

    def _get_key(self, window_size: int) -> str:
        return f"{self.DB_PREFIX}:{self.user_id}:{window_size}"

    def check_and_consume(self) -> bool:
        current_time = int(time.time())
        pipe = self.redis.pipeline()

        for window_size, limit in self.limits:
            key = self._get_key(window_size)
            pipe.incr(key)
            pipe.expire(key, window_size)

        results = pipe.execute()

        for i, (_, limit) in enumerate(self.limits):
            if results[i * 2] > limit:
                return False

        return True

    def get_remaining(self) -> List[int]:
        pipe = self.redis.pipeline()

        for window_size, _ in self.limits:
            key = self._get_key(window_size)
            pipe.get(key)

        results = pipe.execute()

        remaining = []
        for i, (_, limit) in enumerate(self.limits):
            count = int(results[i] or 0)
            remaining.append(max(0, limit - count))

        return remaining
