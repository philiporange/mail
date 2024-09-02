import time
import unittest
from unittest.mock import patch, MagicMock

from redislite import Redis
from src.mail.ratelimiter import RateLimiter

class TestRateLimiter(unittest.TestCase):
    def setUp(self):
        self.redis = Redis()
        self.limits = [(60, 5), (3600, 10)]  # 5 per minute, 10 per hour
        self.rate_limiter = RateLimiter(self.redis, self.limits)

    def tearDown(self):
        self.redis.flushall()

    def test_check_and_consume_within_limits(self):
        for _ in range(5):
            self.assertTrue(self.rate_limiter.check_and_consume())

    def test_check_and_consume_exceeds_limit(self):
        for _ in range(5):
            self.assertTrue(self.rate_limiter.check_and_consume())
        self.assertFalse(self.rate_limiter.check_and_consume())

    def test_get_remaining(self):
        for _ in range(3):
            self.rate_limiter.check_and_consume()

        remaining = self.rate_limiter.get_remaining()
        self.assertEqual(remaining, [2, 7])  # 2 left for minute, 7 for hour

    @patch('time.time')
    def test_window_reset(self, mock_time):
        mock_time.return_value = 1000  # Set initial time

        for _ in range(5):
            self.assertTrue(self.rate_limiter.check_and_consume())
        self.assertFalse(self.rate_limiter.check_and_consume())

        mock_time.return_value = 1061  # Advance time by 61 seconds
        self.assertTrue(self.rate_limiter.check_and_consume())

    def test_multiple_users(self):
        user1_limiter = RateLimiter(self.redis, self.limits, user_id='user1')
        user2_limiter = RateLimiter(self.redis, self.limits, user_id='user2')

        for _ in range(5):
            self.assertTrue(user1_limiter.check_and_consume())
            self.assertTrue(user2_limiter.check_and_consume())

        self.assertFalse(user1_limiter.check_and_consume())
        self.assertFalse(user2_limiter.check_and_consume())

    def test_redis_interaction(self):
        with patch.object(self.redis, 'pipeline', wraps=self.redis.pipeline) as mock_pipeline:
            self.rate_limiter.check_and_consume()
            mock_pipeline.assert_called_once()

            pipeline_instance = mock_pipeline.return_value
            self.assertEqual(pipeline_instance.incr.call_count, 2)
            self.assertEqual(pipeline_instance.expire.call_count, 2)


if __name__ == '__main__':
    unittest.main()
