from sqlalchemy.orm import Session
from datetime import date
import time
from typing import Optional

from models import UserRequestLimit

request_limit_column = {
                        "change_user_email": {"type": "date", "time": 1},
                        "change_avatar": {"type": "date", "time": 1},
                        "change_bio": {"type": "date", "time": 1},
                        "change_user_name": {"type": "date", "time": 1},
                        "submit_feedback": {"type": "date", "time": 1},
                        "send_email": {"type": "tick", "time": 30}
                        }

def check_user_request(db: Session, user_id: int, limit_field: str):
    record = db.query(UserRequestLimit).filter(UserRequestLimit.user_id == user_id,
                                                   UserRequestLimit.request_field == limit_field
                                                   ).with_for_update().first()
    if record:
        if request_limit_column[limit_field]["type"] == "date":
            today = date.today()
            
            delta = today - record.request_date
            if delta.days >= request_limit_column[limit_field]["time"]:
                return False, record
            else:
                return True, None
        elif request_limit_column[limit_field]["type"] == "tick":
            now = int(time.time())
            delta = now- record.request_tick
            if delta.days >= request_limit_column[limit_field]["time"]:
                return False, record
            else:
                return True, None
    else:
        return False, None
                
    

def update_request_record(db: Session, user_id: str, record: Optional[UserRequestLimit], 
                       limit_field: str) -> bool:
    today = date.today()
    now = int(time.time())

    if not record:
        new_recode = UserRequestLimit(user_id = user_id, request_date = today, request_field = limit_field,
                                      request_tick = now)
        db.add(new_recode)
        return True
    else:
        record.request_date = today
        record.request_tick = now
        return True