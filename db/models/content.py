from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base

class Content(Base):
    __tablename__ = "content"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    title = Column(String, index=True, nullable=False)
    path = Column(String, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    workspace_id = Column(Integer, ForeignKey('workspaces.id'), nullable=True)
    created_datetime = Column(DateTime(timezone=True), server_default=func.now())
    updated_datetime = Column(DateTime(timezone=True), onupdate=func.now())
    is_available = Column(Boolean, default=True, nullable=False)

    user = relationship("User", back_populates="content")
    workspace = relationship("Workspace", back_populates="content")