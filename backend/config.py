import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()

ROOT_PATH = os.getenv("ROOT_PATH", "http://localhost:5173")

SECRET_KEY = os.getenv("SECRET_KEY", "leavesberry-helloworld-520")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_AUTH_CODE = os.getenv("EMAIL_AUTH_CODE")

MAX_UPLOADIMG_SIZE = 2 * 1024 * 1024

PUBLIC_DIR = os.path.abspath("./data/static/")

# MySQL 配置
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "LeavesBerry#Zzy")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "leavesberry")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    (
        f"mysql+pymysql://{quote_plus(DB_USER)}:{quote_plus(DB_PASSWORD)}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    ),
)

# Redis 配置：与 MySQL 配置集中放在同一个文件中
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_USERNAME = os.getenv("REDIS_USERNAME")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_SSL = os.getenv("REDIS_SSL", "false").lower() in {"1", "true", "yes"}
REDIS_KEY_PREFIX = os.getenv("REDIS_KEY_PREFIX", "leavesberry")
REDIS_ENABLED = os.getenv("REDIS_ENABLED", "true").lower() in {"1", "true", "yes"}

_redis_scheme = "rediss" if REDIS_SSL else "redis"
_redis_auth = ""
if REDIS_USERNAME and REDIS_PASSWORD:
    _redis_auth = f"{quote_plus(REDIS_USERNAME)}:{quote_plus(REDIS_PASSWORD)}@"
elif REDIS_PASSWORD:
    _redis_auth = f":{quote_plus(REDIS_PASSWORD)}@"

REDIS_URL = os.getenv(
    "REDIS_URL",
    f"{_redis_scheme}://{_redis_auth}{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
)

# 缓存时间（秒），可通过环境变量覆盖
CACHE_TTL_SHORT = int(os.getenv("CACHE_TTL_SHORT", "60"))
CACHE_TTL_MEDIUM = int(os.getenv("CACHE_TTL_MEDIUM", "300"))
CACHE_TTL_LONG = int(os.getenv("CACHE_TTL_LONG", "1800"))
