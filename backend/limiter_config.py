from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Depends
from auth import get_current_user

# 1. 连接Redis
redis_url = "redis://127.0.0.1:6379/0"

def get_user_key(request):
    token = request.headers.get("Authorization", "")
    if token:
        return f"user_{token}"
    # 未登录用户用IP区分
    return f"ip_{get_remote_address(request)}"

# 3. 初始化限流器
limiter = Limiter(key_func=get_user_key, storage_uri=redis_url)

# 全局挂载异常处理器
def init_limiter(app):
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)