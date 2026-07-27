import os
from io import BytesIO
from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageOps, UnidentifiedImageError
from sqlalchemy import update
from sqlalchemy.orm import Session

from cache import cache
from config import PUBLIC_DIR
from exceptions import APIError
from models import UserProfile


AVATAR_MAX_WIDTH = 600
AVATAR_MAX_HEIGHT = 600
AVATAR_JPEG_QUALITY = 85


def _invalidate_user_info(user_id: int) -> None:
    cache.delete(cache.build_key("user", "info", user_id))


def change_xp(user_id: int, change_value: int, db: Session) -> bool:
    change = (
        update(UserProfile)
        .where(UserProfile.user_id == user_id)
        .values(level_xp=UserProfile.level_xp + change_value)
    )
    result = db.execute(change)
    db.commit()

    changed = result.rowcount > 0
    if changed:
        _invalidate_user_info(user_id)
    return changed


def normalize_avatar(file_bytes: bytes) -> bytes:
    """
    验证上传内容确实是图片，并统一转成 RGB JPEG。

    这样可以避免仅依赖文件扩展名，也能移除 EXIF 等不必要元数据。
    """
    if not file_bytes:
        raise APIError("上传文件为空")

    try:
        # verify() 会检查文件结构，但调用后 Image 对象不能继续用于转换，
        # 因此下面需要重新打开一次。
        with Image.open(BytesIO(file_bytes)) as image:
            image.verify()

        with Image.open(BytesIO(file_bytes)) as image:
            image = ImageOps.exif_transpose(image)
            image = image.convert("RGB")
            image.thumbnail(
                (AVATAR_MAX_WIDTH, AVATAR_MAX_HEIGHT),
                Image.Resampling.LANCZOS,
            )

            output = BytesIO()
            image.save(
                output,
                format="JPEG",
                quality=AVATAR_JPEG_QUALITY,
                optimize=True,
            )
            normalized = output.getvalue()

    except Image.DecompressionBombError as exc:
        raise APIError("图片像素尺寸过大") from exc
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise APIError("上传内容不是有效图片") from exc

    if not normalized:
        raise APIError("图片转换失败")

    return normalized

def _local_avatar_path_from_url(avatar_url: str | None):

    if not avatar_url:
        return None

    file_name = (
        avatar_url
        .split("?", 1)[0]
        .rstrip("/")
        .rsplit("/", 1)[-1]
    )

    if (
        not file_name.startswith("avatar_")
        or not file_name.endswith(".jpg")
    ):
        return None

    return Path(PUBLIC_DIR) / "avatar" / file_name

def change_avatar(user_id: int, file_bytes: bytes, db: Session) -> tuple[str, bool]:
    """
    使用唯一文件名保存新头像，再更新数据库。

    保存失败时不会覆盖旧头像；数据库失败时会删除刚写入的新文件。
    数据库成功后再尝试清理旧头像。
    """
    profile = (
        db.query(UserProfile)
        .filter(UserProfile.user_id == user_id)
        .first()
    )
    if not profile:
        return "", False

    public_dir = Path(PUBLIC_DIR)

    avatar_dir = public_dir / "avatar"

    avatar_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    old_avatar_path = _local_avatar_path_from_url(profile.avatar_url)
    file_name = f"avatar_{user_id}_{uuid4().hex}.jpg"
    final_path = avatar_dir / file_name
    temp_path = avatar_dir / f".{file_name}.tmp"
    avatar_url = f"/static/avatar/{file_name}"

    try:
        # 先写临时文件，再通过 os.replace 原子移动到正式文件名。
        with open(temp_path, "wb") as file:
            file.write(file_bytes)
            file.flush()
            os.fsync(file.fileno())

        os.replace(temp_path, final_path)

        profile.avatar_url = avatar_url
        db.commit()

    except Exception:
        db.rollback()

        if temp_path.exists():
            temp_path.unlink(missing_ok=True)
        if final_path.exists():
            final_path.unlink(missing_ok=True)

        raise

    # 数据库更新成功后再删除旧文件。清理失败不影响本次头像更新结果。
    if old_avatar_path and old_avatar_path != final_path:
        try:
            old_avatar_path.unlink(missing_ok=True)
        except OSError:
            pass

    _invalidate_user_info(user_id)
    return avatar_url, True
