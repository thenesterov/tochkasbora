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


class DatabaseOperations:
    def __init__(self, session: Session):
        self.session = session

    def get_user(self, username: str | None = None, email: EmailStr | None = None) -> User | None:
        if not username and not email:
            return None
        try:
            if username:
                user = self.session.query(User).filter(User.username == username).one()
            elif email:
                user = self.session.query(User).filter(User.email == username).one()
        except NoResultFound:
            return None

        return user

    def add(self, object):
        self.session.add(object)
        self.session.commit()

# TODO to setting EXP time
class UserOperations:
    def __init__(self, session: Session = Depends(get_database)):
        self.session = session
        self.database_operations = DatabaseOperations(self.session)

    # TODO if email have been registered, then send an error
    def user_registration(self, user: UserCreate):
        new_user = User(
            email=user.email,
            username=user.username,
            hashed_password=get_password_hash(user.password)
        )

        self.database_operations.add(new_user)

        return self.create_access_token({"sub": new_user.username})  # TODO return a dict with "access_token" and "refresh_token" fields

    # ???
    def get_user(self, username: str | None = None, email: EmailStr | None = None):
        if username:
            user = self.database_operations.get_user(username=username)
        if email:
            user = self.database_operations.get_user(email=email)
        if user:
            user_dict = user.__dict__
            return schemas.UserInDB(**user_dict)

    def authenticate_user(self, username: str, password: str):
        user = self.get_user(username=username)
        if not user:
            return False
        if not verify_password(password, user.hashed_password):
            return False

        return self.create_access_token(data={'sub': user.username})

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(seconds=settings.jwt_expiration)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
        return encoded_jwt

    def validate_access_token(self, token: str = Depends(oauth2_scheme)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        except JWTError:
            raise credentials_exception
        else:
            return payload.get('exp') > datetime.utcnow().timestamp()
