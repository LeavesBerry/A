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
from backend.request_limit import check_user_request, update_user_record
from exceptions import APIError

router = APIRouter()

@router.post("/api/submitFeedBack")
@limiter.limit("1/24hours")
async def submit_feedback(request: Request, 
        data: FeedBackRequest, 
        db: Session = Depends(get_db),
        user_id: int = Depends(get_current_user("user_id"))):
    limit_field = "feedback"
    has_submitted, record = check_user_request(db, user_id, limit_field)

    if has_submitted:
        raise APIError ("一天内只能提交一次反馈")

    else:
        if not update_user_record(db, user_id, record, limit_field):
                raise APIError("一天内只能提交一次反馈")
        send_email(user_email= data.user_email, text_content = data.feedback, 
                                   subject = "user_feedback")
        return JSONResponse({"msg": "提交反馈成功!"})
        
