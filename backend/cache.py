import json
import logging
from typing import Any, Callable, TypeVar

from redis import Redis
from redis.exceptions import RedisError

from config import REDIS_ENABLED, REDIS_KEY_PREFIX, REDIS_URL

logger = logging.getLogger(__name__)
T = TypeVar("T")


class RedisCache:
    """通用 Redis JSON 缓存模块。

    Redis 故障时所有操作都会安全降级，不阻断 MySQL 主流程。
    """

    def __init__(self) -> None:
        self.enabled = REDIS_ENABLED
        self._client: Redis | None = None

        if self.enabled:
            self._client = Redis.from_url(
                REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=1.5,
                socket_timeout=1.5,
                health_check_interval=30,
                retry_on_timeout=True,
            )

    def build_key(self, *parts: object) -> str:
        clean_parts = [str(part).strip(":") for part in parts]
        return ":".join([REDIS_KEY_PREFIX, *clean_parts])

    def ping(self) -> bool:
        if not self.enabled or self._client is None:
            return False
        try:
            return bool(self._client.ping())
        except RedisError as exc:
            logger.warning("Redis ping 失败，应用将使用 MySQL 降级运行: %s", exc)
            return False

    def get(self, key: str, default: T | None = None) -> Any | T | None:
        if not self.enabled or self._client is None:
            return default
        try:
            value = self._client.get(key)
            if value is None:
                return default
            return json.loads(value)
        except (RedisError, json.JSONDecodeError, TypeError) as exc:
            logger.warning("读取 Redis 缓存失败 key=%s: %s", key, exc)
            return default

    def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        if not self.enabled or self._client is None:
            return False
        try:
            payload = json.dumps(
                value,
                ensure_ascii=False,
                separators=(",", ":"),
            )
            if ttl is None:
                return bool(self._client.set(key, payload))
            return bool(self._client.setex(key, ttl, payload))
        except (RedisError, TypeError, ValueError) as exc:
            logger.warning("写入 Redis 缓存失败 key=%s: %s", key, exc)
            return False

    def delete(self, *keys: str) -> int:
        if not keys or not self.enabled or self._client is None:
            return 0
        try:
            return int(self._client.delete(*keys))
        except RedisError as exc:
            logger.warning("删除 Redis 缓存失败 keys=%s: %s", keys, exc)
            return 0

    def delete_pattern(self, pattern: str, batch_size: int = 200) -> int:
        """使用 SCAN 删除匹配键，避免生产环境使用 KEYS 阻塞 Redis。"""
        if not self.enabled or self._client is None:
            return 0

        deleted = 0
        try:
            batch: list[str] = []
            for key in self._client.scan_iter(match=pattern, count=batch_size):
                batch.append(key)
                if len(batch) >= batch_size:
                    deleted += int(self._client.delete(*batch))
                    batch.clear()
            if batch:
                deleted += int(self._client.delete(*batch))
            return deleted
        except RedisError as exc:
            logger.warning("按模式删除 Redis 缓存失败 pattern=%s: %s", pattern, exc)
            return deleted

    def remember(self, key: str, loader: Callable[[], T], ttl: int) -> T:
        """Cache-Aside：缓存命中直接返回，未命中时加载并回填。"""
        sentinel = object()
        cached = self.get(key, sentinel)
        if cached is not sentinel:
            return cached
        value = loader()
        self.set(key, value, ttl)
        return value

    def close(self) -> None:
        if self._client is None:
            return
        try:
            self._client.close()
        except RedisError as exc:
            logger.warning("关闭 Redis 连接失败: %s", exc)


cache = RedisCache()
