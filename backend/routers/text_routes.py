from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database import get_db
from exceptions import APIError
from models import TextRes
from schemas import TextResRequest

router = APIRouter()

@router.post("/api/getTextResourse")
async def get_text_resourse(data: TextResRequest, db: Session = Depends(get_db)):
    name = data.text_name
    text_res = db.query(TextRes).filter(TextRes.name == name).first()
    if text_res:
        return text_res.text
    else:
        raise APIError("未找到文本")