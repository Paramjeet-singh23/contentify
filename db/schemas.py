# schemas.py

from pydantic import BaseModel, EmailStr
from datetime import date
from datetime import datetime

class User(BaseModel):
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    date_of_birth: date

class CreateUser(BaseModel):
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    password: str
    date_of_birth: date

class Token(BaseModel):
    token_type: str
    access_token: str
    refresh_token: str

class CreateWorkspace(BaseModel):
    name: str
    description: str
    api_key: str 
    api_secret: str

class Workspace(BaseModel):
    name: str
    description: str
    owner_id: int

class WorkspaceUserMapping(BaseModel):
    workspace_id: int
    user_id: int
    role: str

# Base schema for Content
class ContentBase(BaseModel):
    name: str
    title: str
    path: str

# Schema to read Content
class Content(ContentBase):
    id: int
    user_id: int
    workspace_id: int
    created_datetime: datetime
    updated_datetime: datetime
    is_available: bool

    class Config:
        form_mode = True

# Schema to create Content
class CreateContent(ContentBase):
    user_id: int
    workspace_id: int

# Schema to update Content
class UpdateContent(ContentBase):
    pass