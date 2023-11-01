from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from db import crud, models, schemas, database
from db.models.user import User
from db.models.utils import RefreshToken
from datetime import timedelta, datetime
from passlib.context import CryptContext
from utils import auth 
from core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFERESH_TOKEN_EXPIRE_MINUTES



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user


def authorize_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not bcrypt_context.verify(password, user.hashed_password):
        return None

    return user


def create_access_token(username: str, user_id: int, expiration_delta: timedelta = timedelta(minutes= ACCESS_TOKEN_EXPIRE_MINUTES)):
    encode = {"sub": username, "id": user_id}
    expires = datetime.utcnow() + expiration_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: int, expiration_delta: timedelta = timedelta(minutes= REFERESH_TOKEN_EXPIRE_MINUTES)):
    token_data = {
        "type": "refresh",
        "user_id": user_id,
        "exp": datetime.utcnow() + expiration_delta
    }
    return jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)


def verify_user(form_data, db: Session):
    user = auth.authorize_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=404, detail="password is wrong")
    
    # Revoke all existing refresh tokens for the user
    existing_tokens = db.query(RefreshToken).filter_by(user_id=user.id).all()
    for token in existing_tokens:
        token.revoked = True
    db.commit()

    access_token = auth.create_access_token(user.username, user.id)
    refresh_token = auth.create_refresh_token(user.id)

    # Store refresh token in the database
    new_refresh_token = RefreshToken(user_id=user.id, token=refresh_token, expires=datetime.utcnow() + timedelta(minutes=REFERESH_TOKEN_EXPIRE_MINUTES))
    db.add(new_refresh_token)
    db.commit()

    token_resp = { "token_type": "Bearer", "access_token": access_token, "refresh_token": refresh_token}
    return token_resp


def create_new_access_token(refresh_token: str, db: Session):
    # verify the refresh token
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token type")

        stored_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token, RefreshToken.revoked == False).first()
        if not stored_token:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token not found")

        # generate a new access token
        user_id = payload.get("user_id")
        user = db.query(User).filter(User.id == user_id).first()
        new_access_token = create_access_token(user.username, user.id)
        token_resp = { "token_type": "Bearer", "access_token": new_access_token, "refresh_token": refresh_token}
        return token_resp
    except JWTError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate refresh token")
    

def logout(refresh_token: str, db: Session):
    # Query for the refresh token in the database
    stored_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()

    # If token is found and not already revoked, set it as revoked
    if stored_token and not stored_token.revoked:
        stored_token.revoked = True
        db.commit()
        return {"detail": "Refresh token has been revoked"}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token not found or already revoked")
