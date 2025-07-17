from cryptography.fernet import Fernet
from sqlalchemy import Column, String, LargeBinary

from .base import Base


class UserInfo(Base):
    __tablename__ = "user_info"

    user_id = Column(String, primary_key=True)
    access_token = Column(LargeBinary, nullable=False)
    refresh_token = Column(LargeBinary, nullable=True)
