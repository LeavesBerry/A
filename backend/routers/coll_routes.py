from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import exists
from sqlalchemy.orm import Session
from limiter_config import limiter

from auth import get_current_user
from cache import cache
from config import CACHE_TTL_MEDIUM, ROOT_PATH
from database import get_db
from models import Coll
from schemas import CollRequest
from services.security import hash_url

router = APIRouter()


def coll_list_cache_key(user_id: int) -> str:
    return cache.build_key("coll", "list", user_id)


def coll_exists_cache_key(user_id: int, url_hash: str) -> str:
    return cache.build_key("coll", "exists", user_id, url_hash)


@router.post("/api/initColl")
@limiter.limit("10/10seconds")
async def init_coll(request: Request, 
    data: CollRequest,
    user_id: int = Depends(get_current_user("user_id")),
    db: Session = Depends(get_db),
):
    url_hash = hash_url(data.url)
    cache_key = coll_exists_cache_key(user_id, url_hash)

    def load_exists():
        return bool(
            db.query(
                exists().where(
                    Coll.user_id == user_id,
                    Coll.url_hash == url_hash,
                )
            ).scalar()
        )

    is_collected = cache.remember(cache_key, load_exists, CACHE_TTL_MEDIUM)
    return JSONResponse({"msg": "ok", "is_collected": is_collected})


@router.post("/api/toggleColl")
@limiter.limit("7/10seconds")
async def toggle_coll(request: Request, 
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
    title = data.title or data.url

    if coll:
        db.delete(coll)
        db.commit()
        cache.delete(
            coll_list_cache_key(user_id),
            coll_exists_cache_key(user_id, url_hash),
        )
        return JSONResponse({"msg": "已取消收藏", "is_collected": False})

    new_coll = Coll(
        user_id=user_id,
        title=title,
        url=data.url,
        url_hash=url_hash,
        type=data.type or "other",
    )
    db.add(new_coll)
    db.commit()
    cache.delete(
        coll_list_cache_key(user_id),
        coll_exists_cache_key(user_id, url_hash),
    )
    return JSONResponse({"msg": "收藏成功", "is_collected": True})


@router.post("/api/getAllColl")
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
                "url": item.url.replace(ROOT_PATH, ""),
                "title": item.title,
                "type": item.type,
            }
            for item in colls
        ]

    result = cache.remember(cache_key, load_coll_list, CACHE_TTL_MEDIUM)
    return JSONResponse(result)
