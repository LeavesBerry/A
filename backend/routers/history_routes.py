from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from limiter_config import limiter

from auth import get_current_user
from cache import cache
from config import CACHE_TTL_SHORT
from database import get_db
from models import History
from schemas import VisitListRequest

router = APIRouter()


def history_cache_key(user_id: int) -> str:
    return cache.build_key("history", user_id)


@router.post("/api/submitVisitList")
@limiter.limit("1/1minute")
def submit_visit_list(request: Request, 
    data: VisitListRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user("user_id")),
):
    history = db.query(History).filter(History.user_id == user_id).first()

    if history is None:
        history = History(user_id=user_id, visit_list=data.visit_list)
        db.add(history)
    else:
        old_visit_list = history.visit_list or []
        history.visit_list = [*old_visit_list, *data.visit_list]

    db.commit()
    cache.delete(history_cache_key(user_id))
    return JSONResponse({"pass": ""})


@router.post("/api/getHistory")
@limiter.limit("10/1minutes")
def get_history(request: Request, 
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user("user_id")),
):
    cache_key = history_cache_key(user_id)

    def load_history():
        history = db.query(History).filter(History.user_id == user_id).first()
        return history.visit_list if history else []

    visit_list = cache.remember(cache_key, load_history, CACHE_TTL_SHORT)
    return JSONResponse({"history": visit_list})
