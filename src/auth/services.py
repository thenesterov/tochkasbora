from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import EmailStr
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta

from starlette import status

from . import schemas
from .models import User
from .schemas import UserCreate, TokenData
from .utils import *
from ..database import get_database
from ..settings import settings

# TODO Move to routers.py
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


class UserOperations:
    def __init__(self, session: Session = Depends(get_database)):
        self.session = session

    # TODO Replace type of email
    def get_user_by_email(self, email: EmailStr) -> User | None:
        try:
            user = self.session.query(User).filter(User.email == email).one()
        except NoResultFound:
            return None

        return user

    def get_user_by_username(self, username: str) -> User | None:
        try:
            user = self.session.query(User).filter(User.username == username).one()
        except NoResultFound:
            return None

        return user

    def user_registration(self, user: UserCreate):
        new_user = User(
            email=user.email,
            username=user.username,
            hashed_password=get_password_hash(user.password)
        )

        self.session.add(new_user)
        self.session.commit()

        return 200

    def get_user(self, username: str):
        user = self.get_user_by_username(username)
        if user:
            user_dict = user.__dict__
            return schemas.UserInDB(**user_dict)

    def authenticate_user(self, username: str, password: str):
        user = self.get_user(username)
        if not user:
            return False
        if not verify_password(password, user.hashed_password):
            return False
        return user

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(seconds=settings.jwt_expiration)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
        return encoded_jwt

    def get_current_user(self, token: str = Depends(oauth2_scheme)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except JWTError:
            raise credentials_exception
        user = self.get_user(username=token_data.username)
        if user is None:
            raise credentials_exception
        return user
