from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from limiter_config import limiter

from auth import get_current_user
from cache import cache
from config import CACHE_TTL_SHORT, MAX_HISTORY_COUNT
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
    history = data.visit_list
    current_history_count = db.query(History).filter(History.user_id == user_id).count()

    add_num  = len(history)

    if current_history_count + add_num > MAX_HISTORY_COUNT:
        need_delete = current_history_count + add_num - MAX_HISTORY_COUNT
        oldest_history = db.query(History).filter(History.user_id == user_id).\
            order_by(History.creat_time.asc()).limit(need_delete).all()

        for item in oldest_history:
            db.delete(item)

    new_record = [History(user_id=user_id, url=item['url'], title=item['title'], type=item['type'],
                          desc=item['desc']) for item in history]

    db.bulk_save_objects(new_record)
    db.commit()


@router.post("/api/getHistory")
@limiter.limit("10/1minutes")
def get_history(request: Request, 
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user("user_id")),
):
    cache_key = history_cache_key(user_id)

    def load_history():
        history = db.query(History).filter(History.user_id == user_id).order_by(History.creat_time.asc()).all()
        return [
                {
                "url": item.url,
                "title": item.title,
                "type": item.type,
                "desc": item.desc
                }
               for item in history 
            ]

    result = cache.remember(cache_key, load_history, CACHE_TTL_SHORT)
    return JSONResponse(result)
