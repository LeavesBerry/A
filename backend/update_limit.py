from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from datetime import date
from typing import Optional

from models import UserUpdateLimit 

def check_user_daily_update(db: Session, user_id: int, limit_field: str, today: date):
    daily_record = db.query(UserUpdateLimit).filter(UserUpdateLimit.user_id == user_id, 
                                                    UserUpdateLimit.update_date == today).with_for_update().first()
    if daily_record:
        updated_list = daily_record.updated_fields
        if limit_field in updated_list:
            return True, None
    return False, daily_record

def update_user_record(db: Session, user_id: str, daily_record: Optional[UserUpdateLimit], 
                       limit_field: str, today: date) -> bool:
    if not daily_record:
        new_recode = UserUpdateLimit(user_id = user_id, update_date = today, updated_fields = [limit_field])
        db.add(new_recode)
        return True
    else:
        updated_list = daily_record.updated_fields
        if limit_field not in updated_list:
            updated_list.append(limit_field)
            daily_record.updated_fields = updated_list
            flag_modified(daily_record, "updated_fields")
            return True
        else:
            return False