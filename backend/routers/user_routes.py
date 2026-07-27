from fastapi import APIRouter, Depends, File, Request, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from auth import get_current_user
from cache import cache
from config import CACHE_TTL_MEDIUM, MAX_UPLOADIMG_SIZE, SERVER_PATH
from database import get_db
from exceptions import APIError
from limiter_config import limiter
from models import UserBase, UserProfile
from schemas import BioRequest
from services.user_service import change_avatar, normalize_avatar


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
            "avatar_url": SERVER_PATH + user_profile.avatar_url,
            "bio": user_profile.bio,
            "level": user_profile.level_xp // 1000,
            "xp": user_profile.level_xp % 1000,
        }

    result = cache.remember(cache_key, load_user_info, CACHE_TTL_MEDIUM)
    return JSONResponse(result)


@router.post("/api/changeBio")
@limiter.limit("2/24hours")
def change_bio(
    request: Request,
    data: BioRequest,
    user_id: int = Depends(get_current_user("user_id")),
    db: Session = Depends(get_db),
):
    user_profile = (
        db.query(UserProfile)
        .filter(UserProfile.user_id == user_id)
        .first()
    )
    if not user_profile:
        raise APIError("用户资料不存在")

    user_profile.bio = data.bio
    db.commit()
    cache.delete(user_info_cache_key(user_id))

    return JSONResponse({"msg": "成功修改个人简介"})


@router.post("/api/changeAvatar")
@limiter.limit("2/24hours")
async def change_user_avatar(
    request: Request,
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user("user_id")),
    db: Session = Depends(get_db),
):
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

    avatar_url, success = change_avatar(
        user_id=user_id,
        file_bytes=normalized_bytes,
        db=db,
    )
    if not success:
        raise APIError("用户资料不存在或头像修改失败")

    return JSONResponse({
        "msg": "修改头像成功",
        "avatar_url": SERVER_PATH + avatar_url,
    })
