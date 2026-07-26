from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from limiter_config import limiter

from cache import cache
from config import CACHE_TTL_LONG
from database import get_db
from exceptions import APIError
from models import TextRes
from schemas import TextResRequest

router = APIRouter()


@router.post("/api/getTextResourse")
@limiter.limit("10/10seconds")
async def get_text_resourse(request: Request, data: TextResRequest, db: Session = Depends(get_db)):
    cache_key = cache.build_key("text_res", data.text_name)

    def load_text():
        text_res = db.query(TextRes).filter(TextRes.name == data.text_name).first()
        if not text_res:
            raise APIError("未找到文本")
        return text_res.text

    return cache.remember(cache_key, load_text, CACHE_TTL_LONG)
