import asyncio
import json
import time

from fastapi import APIRouter, Depends, Request, Header, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from limiter_config import limiter
from collections import defaultdict

from auth import get_current_user
from cache import cache
from config import CACHE_TTL_MEDIUM
from database import get_db
from models import Coll
from schemas import CollRequest
from services.security import hash_url

router = APIRouter()

class CollSSEManager:

    def __init__(self):
        self.connections = defaultdict(
            lambda: defaultdict(set)
        )

    def connect(
        self,
        user_id: int,
        client_id: str,
    ) -> asyncio.Queue:

        queue = asyncio.Queue(
            maxsize=1
        )

        self.connections[
            user_id
        ][
            client_id
        ].add(
            queue
        )

        return queue


    def disconnect(
        self,
        user_id: int,
        client_id: str,
        queue: asyncio.Queue,
    ):

        user_connections = \
            self.connections.get(
                user_id
            )

        if not user_connections:
            return


        client_connections = \
            user_connections.get(
                client_id
            )

        if client_connections:

            client_connections.discard(
                queue
            )

            if not client_connections:

                user_connections.pop(
                    client_id,
                    None
                )

        if not user_connections:

            self.connections.pop(
                user_id,
                None
            )

    def notify_coll_changed(
        self,
        user_id: int,
        source_client_id: str | None,
    ):

        user_connections = \
            self.connections.get(
                user_id
            )

        if not user_connections:
            return


        message = {
            "type": "coll_changed"
        }

        for (
            client_id,
            queues
        ) in list(
            user_connections.items()
        ):

            if (
                source_client_id and
                client_id ==
                    source_client_id
            ):
                continue


            for queue in list(queues):

                if queue.full():
                    continue

                queue.put_nowait(
                    message
                )

coll_sse_manager = CollSSEManager()


def coll_list_cache_key(user_id: int) -> str:
    return cache.build_key("coll", "list", user_id)


@router.post("/api/refreshColl")
@limiter.limit("10/10seconds")
async def refresh_coll(request: Request, 
    data: CollRequest,
    user_id: int = Depends(get_current_user("user_id")),
    db: Session = Depends(get_db),
):
    url_hash = hash_url(data.url)
    coll = (
        db.query(Coll)
        .filter(Coll.user_id == user_id, Coll.url_hash == url_hash)
        .first()
    )

    if not coll:
        return

    if not coll.title == data.title:
        coll.title = data.title
    if not coll.type == data.type:
        coll.type = data.type
    if not coll.desc == data.desc:
        coll.desc = data.desc

    db.commit()
    cache.delete(
        coll_list_cache_key(user_id)
    )
    
@router.post("/api/toggleColl")
@limiter.limit("7/10seconds")
async def toggle_coll(
    request: Request,
    data: CollRequest,

    client_id: str | None = Header(
        default=None,
        alias="X-Client-ID",
    ),

    user_id: int = Depends(
        get_current_user("user_id")
    ),

    db: Session = Depends(
        get_db
    ),
):

    url_hash = hash_url(
        data.url
    )

    coll = (
        db.query(Coll)
        .filter(
            Coll.user_id == user_id,
            Coll.url_hash == url_hash
        )
        .first()
    )

    title = (
        data.title
        or data.url
    )

    if coll:
        db.delete(coll)
        is_collected = False
        msg = "已取消收藏"

    else:
        new_coll = Coll(
            user_id=user_id, title=title, url=data.url, url_hash=url_hash, type=data.type or "other",
            desc=data.desc,)

        db.add(new_coll)

        is_collected = True

        msg = "收藏成功"

    db.commit()
    cache.delete(
        coll_list_cache_key(
            user_id
        )
    )

    coll_sse_manager\
        .notify_coll_changed(
            user_id=user_id,
            source_client_id=
                client_id,
        )

    return JSONResponse({
        "msg": msg,

        "is_collected":
            is_collected
    })

@router.get("/api/collSSE")
async def coll_sse(
    request: Request,
    client_id: str | None = Header(
        default=None,
        alias="X-Client-ID",
    ),
    user_id: int = Depends(
        get_current_user("user_id")
    ),
):

    if not client_id:
        raise HTTPException(
            status_code=400,
            detail="X-Client-ID required",
        )


    queue = coll_sse_manager.connect(
        user_id=user_id,
        client_id=client_id,
    )

    async def event_stream():

        try:
            yield (
                "event: connected\n"
                'data: {"ok": true}\n\n'
            )


            while True:

                try:

                    # 最长 15 秒没有收藏事件
                    message = \
                        await asyncio.wait_for(
                            queue.get(),
                            timeout=15,
                        )


                    data = json.dumps(
                        message,
                        ensure_ascii=False,
                    )


                    yield (
                        "event: coll_changed\n"
                        f"data: {data}\n\n"
                    )


                except asyncio.TimeoutError:

                    if (
                        await request
                            .is_disconnected()
                    ):
                        break


                    # --------------------
                    # SSE 心跳
                    # --------------------

                    heartbeat = json.dumps({
                        "timestamp":
                            int(time.time())
                    })


                    yield (
                        "event: heartbeat\n"
                        f"data: {heartbeat}\n\n"
                    )


        except asyncio.CancelledError:

            raise


        finally:

            coll_sse_manager.disconnect(
                user_id=user_id,
                client_id=client_id,
                queue=queue,
            )


    return StreamingResponse(
        event_stream(),

        media_type=
            "text/event-stream",

        headers={
            "Cache-Control":
                "no-cache",

            "Connection":
                "keep-alive",

            # Nginx 不要缓存 SSE
            "X-Accel-Buffering":
                "no",
        },
    )

@router.get("/api/getAllColl")
@limiter.limit("10/1minute")
async def get_all_coll(request: Request, 
    user_id: int = Depends(get_current_user("user_id")),
    db: Session = Depends(get_db),
):
    cache_key = coll_list_cache_key(user_id)

    def load_coll_list():
        colls = db.query(Coll).filter(Coll.user_id == user_id).all()
        return [
            {
                "url": item.url,
                "title": item.title,
                "type": item.type,
                "desc": item.desc,
            }
            for item in colls
        ]

    result = cache.remember(cache_key, load_coll_list, CACHE_TTL_MEDIUM)
    return JSONResponse(result)
