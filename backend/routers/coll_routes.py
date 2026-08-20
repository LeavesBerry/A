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
            coll_list_cache_key(user_id)
        )
        return JSONResponse({"msg": "已取消收藏", "is_collected": False})

    new_coll = Coll(
        user_id=user_id,
        title=title,
        url=data.url,
        url_hash=url_hash,
        type=data.type or "other",
        desc=data.desc
    )
    db.add(new_coll)
    db.commit()
    cache.delete(
        coll_list_cache_key(user_id)
    )
    return JSONResponse({"msg": "收藏成功", "is_collected": True})


@router.post("/api/getAllCollInfo")
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
