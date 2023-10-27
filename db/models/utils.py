from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from db.database import Base
from datetime import datetime

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    token = Column(String, index=True, unique=True, nullable=False)
    expires = Column(DateTime, index=True, default=datetime.utcnow)
    revoked = Column(Boolean, default=False)
