from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from limiter_config import limiter

from cache import cache
from config import CACHE_TTL_LONG, CACHE_TTL_MEDIUM
from database import get_db
from exceptions import APIError
from models import Anno
from schemas import AnnoRequest

router = APIRouter()

@router.get("/api/getAllAnnoInfo")
#@limiter.limit("5/60minute")
async def get_all_anno_info(request: Request, db: Session = Depends(get_db)):
    cache_key = cache.build_key("anno", "list")

    def load_annos():
        annos = db.query(Anno.title, Anno.type, Anno.id, Anno.anno_date, Anno.desc).all()
        return [
            {
                "title": item.title,
                "type": item.type,
                "desc": item.desc,
                "id": item.id,
                "anno_date": item.anno_date,
            }
            for item in annos
        ]

    result = cache.remember(cache_key, load_annos, CACHE_TTL_MEDIUM)
    return JSONResponse(result)


@router.post("/api/getAnnounceContent")
@limiter.limit("1/1second")
async def get_anno_content(request: Request, data: AnnoRequest, db: Session = Depends(get_db)):
    cache_key = cache.build_key("anno", "detail", data.id)

    def load_anno():
        item = (
            db.query(Anno.id, Anno.title, Anno.main_text, Anno.desc)
            .filter(Anno.id == data.id)
            .first()
        )
        if not item:
            raise APIError("公告不存在")
        return {"main_text": item.main_text, "title": item.title, "desc": item.desc}

    result = cache.remember(cache_key, load_anno, CACHE_TTL_LONG)
    return JSONResponse(result)
