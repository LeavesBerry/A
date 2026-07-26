# backend 拆分说明

启动文件必须放在：

```text
backend/mian.py
```

推荐从 backend 目录启动：

```bash
cd backend
python mian.py
```

也可以使用：

```bash
cd backend
uvicorn mian:app --host 127.0.0.1 --port 5000 --reload
```

## 目录结构

```text
backend/
├── mian.py                  # 后端启动入口，创建 FastAPI app、挂载静态目录、注册路由
├── config.py                # 环境变量、数据库连接、JWT、邮箱、上传限制等配置
├── database.py              # SQLAlchemy engine、SessionLocal、Base、get_db
├── models.py                # 数据库 ORM 模型
├── schemas.py               # Pydantic 请求模型
├── exceptions.py            # APIError 和全局异常处理
├── email_templates.py       # 验证码邮件 HTML 模板
├── auth.py                  # OAuth2/JWT 当前用户依赖
├── routers/
│   ├── __init__.py
│   ├── system.py            # favicon、/api/ping
│   ├── auth_routes.py       # sendCode、register、login、refreshToken、logout
│   ├── user_routes.py       # getUserInfo、changeBio、changeAvatar
│   ├── coll_routes.py       # 收藏相关接口
│   └── anno_routes.py       # 公告接口
└── services/
    ├── __init__.py
    ├── security.py          # 密码哈希、JWT、URL hash
    ├── email_service.py     # 发邮件
    ├── code_service.py      # 验证码限频和清理
    └── user_service.py      # 经验、头像更新
```

## 注意

1. 运行路径建议是 `cd backend && python mian.py`，因为代码里的 `./data/static/` 会按当前工作目录解析。
2. `.env` 可放在 `backend/.env`，至少建议配置：
   - `SECRET_KEY`
   - ``
   - `EMAIL_AUTH_CODE`
   - `DB_USER`
   - `DB_PASSWORD`
   - `DB_HOST`
   - `DB_PORT`
   - `DB_NAME`


## Redis 缓存

Redis 与 MySQL 的配置统一放在 `config.py`，环境变量写在 `.env`。

安装依赖：

```bash
pip install -r requirements.txt
```

本地启动 Redis（Docker 示例）：

```bash
docker run -d --name leavesberry-redis -p 6379:6379 redis:7-alpine
```

缓存采用 Cache-Aside 模式：

1. 读取时先查 Redis。
2. 未命中时查询 MySQL，并将 JSON 结果写入 Redis。
3. 修改数据后删除相关缓存，下次读取自动重建。
4. Redis 连接失败时自动降级到 MySQL，接口仍可使用。

当前已接入缓存的查询：

- 公告列表与公告详情
- 文本资源
- 用户资料
- 收藏状态与收藏列表
- 用户访问历史

通用模块位于 `cache.py`，可使用：

```python
from cache import cache

key = cache.build_key("module", "resource", resource_id)
value = cache.get(key)
cache.set(key, {"data": "example"}, ttl=300)
cache.delete(key)
value = cache.remember(key, loader_function, ttl=300)
```
