# Imports organized by package
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from db import crud, models, schemas
from db.database import SessionLocal, engine, get_db

from utils import auth
from typing import Annotated

# Instantiation
router = APIRouter()

# User Endpoints

@router.post("/user/", response_model=schemas.User)
def create_user(user: schemas.CreateUser, db: Session = Depends(get_db)):
    """Create a new user."""
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@router.get("/user/{username}", response_model=schemas.User)
def get_user_by_username(username: str, current_user: schemas.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Retrieve a user by their username."""
    db_user = crud.get_user_by_username(db, username=username)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Auth Endpoints

@router.post("/login/", response_model=schemas.Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    """Log in and receive an access token."""
    return auth.verify_user(form_data, db)

@router.post("/token/refresh/", response_model=schemas.Token)
async def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    """Refresh the access token using a refresh token."""
    # Verify the refresh token
    return auth.create_new_access_token(refresh_token, db)

@router.post("/logout")
async def revoke_refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """Revoke a refresh token."""
    return auth.logout(refresh_token, db)
