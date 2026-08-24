import time

from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, JSON, Date
from database import Base


class UserBase(Base):
    __tablename__ = "user_base"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_email = Column(String(120), unique=True, nullable=False, index=True)
    user_name = Column(String(80), nullable=False)
    password_hash = Column(String(256), nullable=False)


class UserProfile(Base):
    __tablename__ = "user_profile"

    user_id = Column(
        Integer,
        ForeignKey("user_base.user_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        unique=True,
        index=True,
    )
    avatar_url = Column(
        String(100),
        default="/static/avatar/default_avatar_1.jpg",
        unique=False,
    )
    bio = Column(String(30), default="你好,世界")
    level_xp = Column(Integer, default=1000, nullable=False)
    last_email_index = Column(Integer, nullable=False, default=0)
    black_list = Column(JSON, nullable=True, default=[])

class UserRequestLimit(Base):
    __tablename__ = "user_request_limit"
    
    user_id = Column(
        Integer,
        ForeignKey("user_base.user_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    request_date = Column(Date, nullable=False)
    request_tick = Column(Integer, default=1, nullable=False)
    request_field = Column(String(30), nullable=False, primary_key=True)



class Code(Base):
    __tablename__ = "code"

    user_id = Column(Integer, primary_key=True)
    user_email = Column(String(120), unique=True, nullable=False, index=True)
    code = Column(String(10), unique=True, nullable=False)
    create_time = Column(Integer, default=int(time.time()))


class LimLogin(Base):
    __tablename__ = "lim_login"

    user_ip = Column(String(100), primary_key=True, unique=True, index=True, nullable=False)
    try_times = Column(Integer, default=0, nullable=False)
    lim_start_time = Column(Float, default=0, nullable=False)
    lim_time = Column(Integer, default=0, nullable=False)


class Coll(Base):
    __tablename__ = "coll"

    user_id = Column(Integer, ForeignKey("user_base.user_id"), primary_key=True, nullable=False, index=True)
    url = Column(String(200), nullable=False, primary_key=True)
    url_hash = Column(String(64), nullable=False, index=True)
    title = Column(String(255), default="未知界面", nullable=True)
    type = Column(String(10), default="other", nullable=True)
    desc = Column(String(25), default="未在本站详细注册的界面", nullable=True)

class History(Base):
    __tablename__ = "history"

    user_id = Column(Integer, ForeignKey("user_base.user_id"), nullable=False, index=True)
    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    url = Column(String(200), nullable=False)
    title = Column(String(255), default="未知界面", nullable=False)
    type = Column(String(10), default="other", nullable=False)
    desc = Column(String(25), default="未在本站详细注册的界面", nullable=False)
    creat_time = Column(Integer, default=int(time.time()), index=True)

class Anno(Base):
    __tablename__ = "anno"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    title = Column(String(255), default="公告", nullable=False)
    type = Column(String(10), default="other", nullable=False)
    desc = Column(String(25), default="未在本站详细注册的界面", nullable=False)
    main_text = Column(Text(), nullable=False)
    anno_date = Column(Integer, nullable=False)


class Email(Base):
    __tablename__ = "email"

    user_id = Column(Integer, ForeignKey("user_base.user_id"), nullable=False, index=True)
    email_index = Column(Integer, nullable=False, index=True)
    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    title = Column(String(255), default="邮件", nullable=False)
    type = Column(String(10), default="other", nullable=False)
    desc = Column(String(25), default="未在本站详细注册的界面", nullable=False)
    main_text = Column(Text(), nullable=False)
    email_date = Column(Integer, nullable=False)

class Pages(Base):
    __tablename__ = "pages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(100), unique=True, nullable=False)
    title = Column(String(255), default="未知界面", nullable=False)
    type = Column(String(10), default="other", nullable=False)
    desc = Column(String(25), default="未在本站详细注册的界面", nullable=False)

class TextRes(Base):
    __tablename__ = "text_res"

    id = Column(Integer,primary_key=True, autoincrement=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    text = Column(JSON, nullable=False)