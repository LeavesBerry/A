import re
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator, model_validator


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

class EmailGetRequest(BaseModel):
    id: int

class EmailSendRequest(BaseModel):
    email_text: str
    email_title: str
    recipient_id: Optional[int] = None
    recipient_email: Optional[str] = None

    @model_validator(mode="after")
    def check_one_field_required(self):
        if self.recipient_email is None and self.recipient_id is None:
            raise ValueError("无法指定用户")
        if self.recipient_email:
            EmailStr(self.recipient_email)
        return self

class FeedBackRequest(BaseModel):
    user_email: EmailStr
    feedback: str

class TextResRequest(BaseModel):
    text_name: str

class VisitListRequest(BaseModel):
    visit_list: list[str]


