from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from db.database import Base
from sqlalchemy.sql import func



class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    hashed_api_key = Column(String)
    hashed_api_secret = Column(String)
    create_datetime = Column(DateTime(timezone=True), server_default=func.now())
    update_datetime = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship with User model
    owner = relationship("User", back_populates="workspaces")
    content = relationship("Content", back_populates="workspace")



class WorkspaceUserMapping(Base):
    __tablename__ = "workspace_user_mapping"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey('workspaces.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    role = Column(Enum('owner', 'editor', name="role_enum"), nullable=False)