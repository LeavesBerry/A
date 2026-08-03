from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from limiter_config import limiter

from cache import cache
from config import CACHE_TTL_LONG, CACHE_TTL_MEDIUM
from database import get_db
from exceptions import APIError
from models import Email
from schemas import EmailRequest
from auth import get_current_user

router = APIRouter()

@router.post("/api/getAllEmail")
@limiter.limit("5/60minute")
async def get_all_anno_info(request: Request, db: Session = Depends(get_db)):
    cache_key = cache.build_key("email", "list")

    def load_annos():
        emails = db.query(Email.title, Email.type, Email.id, Email.email_date).all()
        return [
            {
                "title": item.title,
                "type": item.type,
                "id": item.id,
                "anno_date": item.anno_date,
            }
            for item in emails
        ]

    result = cache.remember(cache_key, load_annos, CACHE_TTL_MEDIUM)
    return JSONResponse(result)


@router.post("/api/getEmailText")
@limiter.limit("1/1second")
async def get_anno_text(request: Request, data: EmailRequest, 
                        db: Session = Depends(get_db), user_id = Depends(get_current_user("user_id"))):
    cache_key = cache.build_key("email", "detail", data.id)

    def load_anno():
        item = (
            db.query(Email.user_id ,Email.id, Email.title, Email.main_text)
            .filter(Email.id == data.id, Email.user_id == user_id)
            .first()
        )
        if not item:
            raise APIError("邮件不存在")
        return {"main_text": item.main_text, "title": item.title}

    result = cache.remember(cache_key, load_anno, CACHE_TTL_LONG)
    return JSONResponse(result)
