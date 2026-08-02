import re
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


class SendCodeRequest(BaseModel):
    user_email: EmailStr


class RegisterRequest(BaseModel):
    user_name: str
    user_email: EmailStr
    code: str
    password: str

    @field_validator("password")
    def validate_password(cls, value):
        if len(value) < 8 or not re.search(r"[A-Za-z]", value) or not re.search(r"[0-9]", value):
            raise ValueError("密码必须8位以上，包含字母+数字")
        return value


class LoginRequest(BaseModel):
    user_email: EmailStr
    password: str


class BioRequest(BaseModel):
    bio: str

class UserNameRequest(BaseModel):
    user_name: str


class CollRequest(BaseModel):
    url: str
    title: Optional[str] = None
    type: Optional[str] = None

    @field_validator("url")
    def validate_url(cls, value):
        if not value or len(value) > 1000:
            raise ValueError("URL不合法")
        return value
    
class AnnoRequest(BaseModel):
    id: int

class FeedBackRequest(BaseModel):
    user_email: EmailStr
    feedback: str

class TextResRequest(BaseModel):
    text_name: str

class VisitListRequest(BaseModel):
    visit_list: list[str]


