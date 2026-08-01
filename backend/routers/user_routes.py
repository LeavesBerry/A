from fastapi import APIRouter, Depends, File, Request, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import date

from auth import get_current_user
from cache import cache
from config import CACHE_TTL_MEDIUM, MAX_UPLOADIMG_SIZE, SERVER_PATH
from database import get_db
from exceptions import APIError
from limiter_config import limiter
from models import UserBase, UserProfile, UserUpdateLimit
from schemas import BioRequest
from services.user_service import change_avatar, normalize_avatar
from update_limit import check_user_daily_update, update_user_record

router = APIRouter()

ALLOWED_AVATAR_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


def user_info_cache_key(user_id: int) -> str:
    return cache.build_key("user", "info", user_id)


@router.post("/api/getUserInfo")
@limiter.limit("1/10minutes")
def get_user_info(
    request: Request,
    user: UserBase = Depends(get_current_user("user")),
    db: Session = Depends(get_db),
):
    cache_key = user_info_cache_key(user.user_id)

    def load_user_info():
        user_profile = (
            db.query(UserProfile)
            .filter(UserProfile.user_id == user.user_id)
            .first()
        )
        if not user_profile:
            raise APIError("用户资料不存在")

        return {
            "is_logined": True,
            "user_id": user.user_id,
            "user_name": user.user_name,
            "user_email": user.user_email,
            "avatar_url":  f'{user_profile.avatar_url}' if SERVER_PATH in user_profile.avatar_url else f'{SERVER_PATH}{user_profile.avatar_url}',
            "bio": user_profile.bio,
            "level": user_profile.level_xp // 1000,
            "xp": user_profile.level_xp % 1000,
        }

    result = cache.remember(cache_key, load_user_info, CACHE_TTL_MEDIUM)
    return JSONResponse(result)


@router.post("/api/changeBio")
@limiter.limit("1/10seconds")
def change_bio(
    request: Request,
    data: BioRequest,
    user_id: int = Depends(get_current_user("user_id")),
    db: Session = Depends(get_db),
):
    
    today = date.today()
    limit_field = "bio"

    has_updated, daily_record = check_user_daily_update(db, user_id, limit_field, today)

    if has_updated:
        raise APIError("今日已更新过简介")

    user_profile = (
        db.query(UserProfile)
        .filter(UserProfile.user_id == user_id)
        .first()
    )

    bio = data.bio

    if not user_profile:
        raise APIError("用户资料不存在")

    if not bio or not type(bio) == str:
        raise APIError("简介格式错误")

    if len(bio) > 20:
        bio = bio[0:21]
    
    if not update_user_record(db, user_id, daily_record, limit_field, today):
        raise APIError("今日已更新过简介")
    
    user_profile.bio = bio
    db.commit()
    cache.delete(user_info_cache_key(user_id))

    return JSONResponse({"msg": "成功修改个人简介"})


@router.post("/api/changeAvatar")
@limiter.limit("1/10seconds")
async def change_user_avatar(
    request: Request,
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user("user_id")),
    db: Session = Depends(get_db),
):

    today = date.today()
    limit_field = "avatar"

    has_updated, daily_record = check_user_daily_update(db, user_id, limit_field, today)

    if has_updated:
        raise APIError("今日已更新过头像")
    
    if file.content_type not in ALLOWED_AVATAR_CONTENT_TYPES:
        raise APIError("不支持该文件类型")

    # 最多读取限制值 + 1 字节，避免超大请求完整进入内存。
    file_bytes = await file.read(MAX_UPLOADIMG_SIZE + 1)
    await file.close()

    if not file_bytes:
        raise APIError("上传文件为空")

    if len(file_bytes) > MAX_UPLOADIMG_SIZE:
        raise APIError("图片文件过大")

    normalized_bytes = normalize_avatar(file_bytes)

    # 重新编码后再次限制文件大小。
    if len(normalized_bytes) > MAX_UPLOADIMG_SIZE:
        raise APIError("处理后的图片文件过大")

    if not update_user_record(db, user_id, daily_record, limit_field, today):
            raise APIError("今日已更新过头像")

    avatar_url, success = change_avatar(
        user_id=user_id,
        file_bytes=normalized_bytes,
        db=db,
    )
    if not success:
        raise APIError("用户资料不存在或头像修改失败")

    return JSONResponse({
        "msg": "修改头像成功",
        "avatar_url": f'{avatar_url}' if SERVER_PATH in avatar_url else f'{SERVER_PATH}{avatar_url}',
    })
