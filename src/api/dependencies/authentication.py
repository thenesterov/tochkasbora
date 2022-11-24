from datetime import datetime, timedelta

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from pydantic import EmailStr
from starlette import status

from src.models.schemas.authentication import UserAuth, UserInDB
from src.db.models.authenticate import User
from src.services.authenticate import get_password_hash, verify_password
from src.db.events import get_database
from src.core.settings import settings


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
                user = self.session.query(User).filter(User.email == email).one()
        except NoResultFound:
            return None

        return user

    def add(self, sqlalchemy_object):
        self.session.add(sqlalchemy_object)
        self.session.commit()


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(seconds=settings.jwt_expiration)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def validate_access_token(token: str = Depends(OAuth2PasswordBearer(tokenUrl='auth/token'))):
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


class UserOperations:
    def __init__(self, session: Session = Depends(get_database)):
        self.session = session
        self.database_operations = DatabaseOperations(self.session)

    def user_registration(self, user: UserAuth):
        new_user = User(
            email=user.email,
            username=user.username,
            hashed_password=get_password_hash(user.password)
        )

        self.database_operations.add(new_user)

        return {
            'access_token': create_access_token({"sub": new_user.username}),
            'refresh_token': ''
        }

    # ???
    def get_user(self, username: str | None = None, email: EmailStr | None = None):
        user = None

        if username:
            user = self.database_operations.get_user(username=username)
        if email:
            user = self.database_operations.get_user(email=email)
        if user:
            user_dict = user.__dict__
            return UserInDB(**user_dict)

    def authenticate_user(self, username: str, password: str):
        user = self.get_user(username=username)

        if not user:
            return False
        if not verify_password(password, user.hashed_password):
            return False

        return {
            'access_token': create_access_token({'sub': user.username}),
            'refresh_token': ''
        }
