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
async def get_all_email_info(request: Request, db: Session = Depends(get_db), 
                             user_id: int = Depends(get_current_user("user_id"))):
    cache_key = cache.build_key("email", "list")

    def load_emails():
        emails = db.query(Email.title, Email.type, Email.id, Email.email_date).filter(Email.user_id == user_id).all()
        return [
            {
                "title": item.title,
                "type": item.type,
                "id": item.id,
                "email_date": item.email_date,
            }
            for item in emails
        ]

    print(load_emails())

    result = cache.remember(cache_key, load_emails, CACHE_TTL_MEDIUM)
    return JSONResponse(result)


@router.post("/api/getEmailText")
@limiter.limit("1/1second")
async def get_email_text(request: Request, data: EmailGetRequest, 
                        db: Session = Depends(get_db), user_id = Depends(get_current_user("user_id"))):
    cache_key = cache.build_key("email", "detail", data.id)

    def load_email():
        item = (
            db.query(Email.user_id ,Email.id, Email.title, Email.main_text)
            .filter(Email.id == data.id, Email.user_id == user_id)
            .first()
        )
        if not item:
            raise APIError("邮件不存在")
        return {"main_text": item.main_text, "title": item.title}

    result = cache.remember(cache_key, load_email, CACHE_TTL_LONG)
    return JSONResponse(result)

@router.post("/api/sendEmail")
@limiter.limit("1/5seconds")
async def send_email(request: Request, data: EmailSendRequest,
                     db: Session = Depends(get_db), user_id = Depends(get_current_user("user_id"))):
    limit_field = "send_email"
    has_sent, record = check_user_request(db, user_id, limit_field)

    if has_sent:
        raise APIError("邮件发送过于频繁")

    if len(data.email_text) > 1000:
        data.email_text = data.email_text[0:1001]

    if len(data.email_title) > 100:
        data.email_title = data.email_title[0:101]

    recipient_email = data.recipient_email
    recipient_id = data.recipient_id

    if recipient_email and recipient_id is None:
        recipient = db.query(UserBase.user_email, UserBase.user_id).filter(UserBase.user_email == data.recipient_email)
        recipient_id = recipient.user_id

    recipient_info = db.query(UserProfile.last_email_index, 
                              UserProfile.black_list).filter(UserProfile.user_id == recipient_id).first()

    if recipient_info is None:
        raise APIError("未找到对应用户")
    
    if not update_request_record(db, user_id, record, limit_field):
        raise APIError("邮件发送过于频繁")

    d = date.today()

    new_email = Email(user_id = recipient_id, id = recipient_info.last_email_index + 1, 
                      title = data.email_title, main_text = data.email_text, 
                      type = "user" if str(user_id) not in recipient_info.black_list else "blacker", 
                      email_date = d.year * 10000 + d.month * 100 + d.day)

    db.add(new_email)
    db.commit()
    cache.delete(user_info_cache_key(recipient_id))

    return JSONResponse({"msg": f'成功给{recipient_id}号用户发送邮件'})