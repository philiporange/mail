from redislite import Redis

from .config import Config


kv = Redis(Config.KV_PATH)
