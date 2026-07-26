import time

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models import FeedBack
from schemas import FeedBackRequest
from services.email_service import send_email
from limiter_config import limiter

router = APIRouter()

@router.post("/api/submitFeedBack")
@limiter.limit("1/24hours")
async def submit_feedback(request: Request, 
        data: FeedBackRequest, 
        db: Session = Depends(get_db),
        user_id: int = Depends(get_current_user("user_id"))):
    user_email = data.user_email
    now = time.time()
    user_feedback_info = db.query(FeedBack).filter(FeedBack.user_email == user_email).first()
    if not user_feedback_info:
        new_feedback_info = FeedBack(user_email=user_email, last_submit_time=now)
        db.add(new_feedback_info)
        send_email(user_email= user_email, text_content = data.feedback, 
                           subject = "user_feedback")
        db.commit()
        return JSONResponse({"msg": "已成功提交反馈"})
    elif user_feedback_info.last_submit_time - now >= 86400:
        user_feedback_info.last_submit_time = now
        send_email(user_email= user_email, text_content = data.feedback, 
                   subject = "user_feedback")
        db.commit()
        return JSONResponse({"msg": "已成功提交反馈"})
    else:
        return JSONResponse({"error": "24小时内只能提交一次反馈"})
