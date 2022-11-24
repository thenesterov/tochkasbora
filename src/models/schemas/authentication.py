from pydantic import BaseModel, EmailStr


class UserAuth(BaseModel):
    email: EmailStr
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserInDB(BaseModel):
    id: int
    email: EmailStr
    username: str
    hashed_password: str
