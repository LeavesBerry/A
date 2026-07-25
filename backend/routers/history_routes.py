from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import update

from auth import get_current_user
from database import get_db
from models import History
from schemas import VisitListRequest
from exceptions import APIError

router = APIRouter()

@router.post('/api/submitVisitList')
def submit_visit_list(
    data: VisitListRequest, 
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user("user_id"))):
    history = (
        db.query(History)
        .filter(History.user_id == user_id)
        .first()
    )

    if history is None:
        history = History(
            user_id=user_id,
            visit_list=data.visit_list
        )
        db.add(history)
    else:
        old_visit_list = history.visit_list or []
        history.visit_list = old_visit_list + data.visit_list

    db.commit()
    db.refresh(history)

    return JSONResponse({"pass":""})

@router.post('/api/getHistory')
def get_history(db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user("user_id"))):
    history = db.query(History).filter(History.user_id == user_id).all()
    return JSONResponse({"history": history})