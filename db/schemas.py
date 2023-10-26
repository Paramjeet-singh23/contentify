# schemas.py

from pydantic import BaseModel, EmailStr
from datetime import date

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
