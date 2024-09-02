import os

import dotenv


dotenv.load_dotenv()


SRC_DIR = os.path.dirname(os.path.abspath(__file__))

# Load environment variables
SES_SENDER = os.environ.get("SES_SENDER")  # Email address to send from
SES_REGION = os.environ.get("SES_REGION")  # AWS SES region
if not SES_SENDER or not SES_REGION:
    raise ValueError("SOURCE_EMAIL and SES_REGION must be set in the environment")

# Default values
KV_PATH = "kv.db"
CHARSET = "UTF-8"
MAX_EMAILS = 2000
TEMPLATES_DIR = os.path.join(SRC_DIR, 'templates')
LIMITS = [(3600, 20), (86400, 100)]     # 20/hour, 100/day

LOG_PATH = "mail.log"
LOG_ROTATION = "1 week"
LOG_RETENTION = "7 days"
LOG_LEVEL = "DEBUG"


class Config:
    KV_PATH = KV_PATH

    SES_REGION = SES_REGION
    SES_SENDER = SES_SENDER
    CHARSET = CHARSET
    MAX_EMAILS = MAX_EMAILS
    TEMPLATES_DIR = TEMPLATES_DIR
    LIMITS = LIMITS

    LOG_PATH = LOG_PATH
    LOG_RETENTION = LOG_RETENTION
    LOG_ROTATION = LOG_ROTATION
    LOG_LEVEL = LOG_LEVEL
