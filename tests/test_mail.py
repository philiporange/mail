import unittest
from src.mail.mail import Mail, MailException

from redislite import Redis


class TestMail(unittest.TestCase):
    def setUp(self):
        self.redis = Redis()
        self.mail = Mail(redis_conn=self.redis)

    def tearDown(self):
        self.redis.flushall()

    def test_invalid_email(self):
        with self.assertRaises(MailException):
            self.mail.send("invalid_email", "Test Subject", "Test Message")

    def test_confirmation_code(self):
        email = "test@example.com"
        code = self.mail.send_confirmation_code(email)

        self.assertEqual(len(code), 6)
        self.assertTrue(code.isdigit())

        # Verify the code
        self.assertTrue(self.mail.verify_confirmation_code(email, code))
        self.assertFalse(self.mail.verify_confirmation_code(email, "wrong_code"))
        self.assertFalse(self.mail.verify_confirmation_code("wrong@email.com", code))


if __name__ == "__main__":
    unittest.main()
