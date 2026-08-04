from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from limiter_config import limiter
from datetime import date

from cache import cache
from config import CACHE_TTL_LONG, CACHE_TTL_MEDIUM
from database import get_db
from exceptions import APIError
from models import Email, UserBase, UserProfile
from schemas import EmailGetRequest, EmailSendRequest
from auth import get_current_user
from request_limit import check_user_request, update_request_record

router = APIRouter()

def user_info_cache_key(user_id: int) -> str:
    return cache.build_key("user", "info", user_id)

@router.post("/api/getAllEmailInfo")
@limiter.limit("5/60minute")
async def get_all_email_info(request: Request, db: Session = Depends(get_db)):
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
async def get_anno_text(request: Request, data: EmailGetRequest, 
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

@router.post("/api/sendEmail")
@limiter.limit("1/5seconds")
async def send_email(request: Request, data: EmailSendRequest,
                     db: Session = Depends(get_db), user_id = Depends(get_current_user("user_id"))):
    limit_field = "send_email"
    has_sent, record = check_user_request(db, user_id, limit_field)

    if has_sent:
        raise APIError("邮件发送过于频繁")

    recipient_email = data.recipient_email
    recipient_id = data.recipient_id

    if recipient_email and recipient_id is None:
        recipient = db.query(UserBase.user_email, UserBase.user_id).filter(UserBase.user_email == data.recipient_email)
        recipient_id = recipient.user_id

    last_email_index = db.query(UserProfile).filter(UserProfile.user_id == recipient_id).first()

    if not last_email_index:
        raise APIError("未找到对应用户")
    
    if not update_request_record(db, user_id, record, limit_field):
        raise APIError("邮件发送过于频繁")

    new_email = Email(user_id = recipient_id, id = last_email_index + 1, title = EmailSendRequest.emiil_title,
                      type = "user", main_text = EmailSendRequest.email_text, email_date = date.today())

    db.add(new_email)
    db.commit()
    cache.delete(user_info_cache_key(recipient_id))

    return JSONResponse({"msg": f'成功给{recipient_id}号用户发送邮件'})