import random
import time
from typing import Optional

from fastapi import APIRouter, Depends, Request, Response, Cookie, HTTPException, status
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from limiter_config import limiter

from config import REFRESH_TOKEN_EXPIRE_DAYS, SECRET_KEY, ALGORITHM
from database import get_db
from email_templates import VERIFYCODEHTML
from exceptions import APIError
from models import Code, LimLogin, UserBase, UserProfile
from schemas import LoginRequest, RegisterRequest, SendCodeRequest
from services.code_service import check_code_rate, clean_expired_codes
from services.email_service import send_email
from services.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)

router = APIRouter()


@router.post("/api/sendCode")
@limiter.limit("1/5minutes")
async def send_code(request: Request, data: SendCodeRequest, db: Session = Depends(get_db)):
    await check_code_rate(data.user_email, db)
    clean_expired_codes(db)

    old_code = db.query(Code).filter(Code.user_email == data.user_email).first()
    if old_code:
        db.delete(old_code)
        db.commit()

    while True:
        code = str(random.randint(100000, 999999))
        try:
            new_code = Code(user_email=data.user_email, code=code, create_time=int(time.time()))
            db.add(new_code)
            db.commit()
            break
        except IntegrityError:
            db.rollback()
            continue

    res, det = send_email(
        data.user_email,
        "LeavesBerry验证码",
        f"验证码：{code}",
        VERIFYCODEHTML.replace("{{CODE}}", code),
    )
    if res:
        return JSONResponse({"msg": "验证码已发送"})
    return JSONResponse({"msg": f"验证码发送失败,因为:{det}"})


@router.post("/api/register")
@limiter.limit("3/5minutes")
async def register(request: Request, data: RegisterRequest, db: Session = Depends(get_db)):
    clean_expired_codes(db)

    code_record = db.query(Code).filter(Code.user_email == data.user_email).first()
    if not code_record or code_record.code != data.code:
        return JSONResponse("验证码错误")
    if time.time() - code_record.create_time > 300:
        print(time.time(), code_record.create_time)
        db.delete(code_record)
        db.commit()
        raise APIError("验证码已过期")

    exist = db.query(UserBase.user_email).filter(UserBase.user_email == data.user_email).first()
    if exist:
        raise APIError("用户已存在")

    user = UserBase(
        user_email=data.user_email,
        user_name=data.user_name,
        password_hash=hash_password(data.password),
        black_list = []
    )
    db.add(user)
    db.flush()

    user_profile = UserProfile(user_id=user.user_id, level_xp=1050)
    db.add(user_profile)
    db.delete(code_record)
    db.commit()

    return JSONResponse({"msg": "注册成功", "xpChange": 50})


@router.post("/api/login")
@limiter.limit("5/5minutes")
async def login(
    request: Request,
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    user = db.query(UserBase).filter(UserBase.user_email == data.user_email).first()
    if not user:
        raise APIError("用户不存在")

    ip = request.client.host
    lim = db.query(LimLogin).filter(LimLogin.user_ip == ip).first()
    if not lim:
        lim = LimLogin(user_ip=ip)
        db.add(lim)
        db.commit()

    now = time.time()
    if now < lim.lim_start_time + lim.lim_time:
        raise APIError("登录过于频繁，请稍后再试")

    if not verify_password(data.password, user.password_hash):
        lim.try_times += 1
        if lim.try_times >= 5:
            lim.lim_start_time = now
            lim.lim_time = 300
            lim.try_times = 0
        db.commit()
        raise APIError("密码错误")

    lim.try_times = 0
    db.commit()

    access_token = create_access_token({"sub": str(user.user_id)})
    refresh_token = create_refresh_token({"sub": str(user.user_id)})

    response = JSONResponse(
        {"msg": f"欢迎回来，{user.user_name}", "access_token": access_token}
    )
    response.set_cookie(
        key="refresh_cookie",
        value=refresh_token,
        expires=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=True,
        secure=False,
        samesite="lax",
        path="/",
    )
    return response


@router.post("/api/refreshToken")
@limiter.limit("2/10minutes")
async def refresh_token(request: Request, 
    refresh_cookie: Optional[str] = Cookie(default=None),
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="登录已失效",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not refresh_cookie:
        raise credentials_exception

    try:
        payload = jwt.decode(refresh_cookie, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise credentials_exception

        user_id = payload.get("sub")
        if not user_id:
            raise credentials_exception

        user = db.query(UserBase).filter(UserBase.user_id == int(user_id)).first()
        if not user:
            raise credentials_exception

        new_access_token = create_access_token({"sub": str(user.user_id)})
        return {"access_token": new_access_token}
    except JWTError:
        raise credentials_exception


@router.post("/api/logout")
@limiter.limit("2/10minutes")
def logout(request: Request, response: Response):
    response.delete_cookie(key="refresh_cookie", path="/")
    return JSONResponse({"msg": "已退出登录"})
