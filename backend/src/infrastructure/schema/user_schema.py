from sqlalchemy import Column, String

from .base import Base


class UserInfo(Base):
    __tablename__ = "user_info"

    user_id = Column(String, primary_key=True)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=True)
