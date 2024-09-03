import os
import random
from typing import Optional

import boto3
import chevron
import premailer
from redislite import Redis
from validate_email import validate_email

from .config import Config
from .db import kv
from .logging import logger
from .ratelimiter import RateLimiter


CHARSET = Config.CHARSET
LIMITS = Config.LIMITS
SES_REGION = Config.SES_REGION
SES_SENDER = Config.SES_SENDER
TEMPLATES_DIR = Config.TEMPLATES_DIR


class MailException(Exception):
    pass


class Mail:
    def __init__(
        self,
        redis_conn: Optional[Redis] = kv,
        source_addr: str = SES_SENDER,
        limits: list = LIMITS,
    ):
        self.redis = redis_conn
        self.source_addr = source_addr
        self.client = boto3.client("ses", region_name=SES_REGION)
        self.templates_dir = TEMPLATES_DIR
        self.template_cache = {}

        self.rate_limiter = RateLimiter(
            self.redis, limits
        )  # Example: 100/hour, 1000/day

    def send(
        self,
        to: str,
        subject: str,
        msg: Optional[str] = None,
        html: Optional[str] = None,
    ) -> dict:
        if not validate_email(to):
            raise MailException("Invalid email address")

        if not self.rate_limiter.check_and_consume():
            raise MailException("Rate limit exceeded")

        destination = {"ToAddresses": [to]}
        message = {"Subject": {"Charset": Config.CHARSET, "Data": subject}, "Body": {}}

        if html:
            message["Body"]["Html"] = {"Charset": Config.CHARSET, "Data": html}
        elif msg:
            message["Body"]["Text"] = {"Charset": Config.CHARSET, "Data": msg}
        else:
            raise MailException("No message content")

        logger.info(f"Sending email to {to}")

        return self.client.send_email(
            Destination=destination,
            Message=message,
            Source=self.source_addr,
        )

    def send_template(self, template: str, to: str, subject: str, data: dict) -> dict:
        template_html = self.build_template(template)
        html = chevron.render(template_html, data)
        return self.send(to, subject, html=html)

    def build_template(self, name: str) -> str:
        if name not in self.template_cache:
            base_html = self._load_template("base")
            main_html = self._load_template(name)
            html = chevron.render(
                base_html,
                {
                    "main": main_html,
                    "summary": "{{{ summary }}}",
                },
            )
            html = premailer.transform(html, preserve_handlebar_syntax=True)
            self.template_cache[name] = html
        return self.template_cache[name]

    def _load_template(self, name: str) -> str:
        path = os.path.join(self.templates_dir, f"{name}.html")
        if not os.path.isfile(path):
            raise MailException("Template doesn't exist")
        with open(path, "r") as fp:
            return fp.read()

    def send_confirmation_code(self, to: str) -> str:
        code = self._generate_confirmation_code()
        self.redis.setex(f"confirmation:{to}", 3600, code)  # Store for 1 hour
        self.send_template(
            "confirmation",
            to,
            "Email Confirmation",
            {"summary": "Confirm your email address", "confirmation_code": code},
        )
        return code

    def verify_confirmation_code(self, email: str, code: str) -> bool:
        stored_code = self.redis.get(f"confirmation:{email}")
        if stored_code and stored_code.decode() == code:
            self.redis.delete(f"confirmation:{email}")
            return True
        return False

    @staticmethod
    def _generate_confirmation_code() -> str:
        return "".join(random.choices("0123456789", k=6))
