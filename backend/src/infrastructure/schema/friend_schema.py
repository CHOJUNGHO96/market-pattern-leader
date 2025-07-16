from sqlalchemy import Column, ForeignKey, String

from .base import Base


class Friend(Base):
    __tablename__ = "friends"

    user_id = Column(String, ForeignKey("user_info.user_id"), primary_key=True)
    friend_id = Column(String, ForeignKey("user_info.user_id"), primary_key=True)
