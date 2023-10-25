# db/models/User.py

from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base
from enum import Enum as PyEnum

class UserGroupEnum(PyEnum):
    ADMIN = "admin"
    OWNER = "owner"
    EDITOR = "editor"
    USER = "user"

class UserGroup(Base):
    __tablename__ = "user_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Enum(UserGroupEnum), unique=True)

    users = relationship("User", back_populates="group")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, index=True, nullable=False)
    last_name = Column(String, index=True, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    create_datetime = Column(DateTime(timezone=True), server_default=func.now())
    update_datetime = Column(DateTime(timezone=True), onupdate=func.now())
    group_id = Column(Integer, ForeignKey('user_groups.id'))
    group = relationship(UserGroup, back_populates="users")
