from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserBase(BaseModel):
    id: int
    email: EmailStr
    username: str


#TODO Изменить тип dict на тип токена
class User(UserBase):
    token: dict = {}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserInDB(User):
    hashed_password: str
