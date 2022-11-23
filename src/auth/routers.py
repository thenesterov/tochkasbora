from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from .schemas import *
from .services import UserOperations, validate_access_token

auth_router = APIRouter(
    prefix='/auth'
)


@auth_router.post('/sign-up')
def sign_up(user: UserAuth, user_operation: UserOperations = Depends()):
    if user_operation.get_user(email=user.email):
        raise HTTPException(status_code=400, detail='Email already registered')
    elif user_operation.get_user(username=user.username):
        raise HTTPException(status_code=400, detail='Username already registered')
    return user_operation.user_registration(user)


@auth_router.post('/sign-in')
def sign_in(user: UserAuth, user_operation: UserOperations = Depends()):
    jwt = user_operation.authenticate_user(username=user.username, password=user.password)
    if jwt:
        return jwt
    else:
        raise HTTPException(status_code=400, detail='Login or password is not correct')


@auth_router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), user_operations: UserOperations = Depends()):
    user = user_operations.authenticate_user(username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"access_token": user["access_token"], "token_type": "bearer"}


@auth_router.get('/is-auth')
def is_auth(authed=Depends(validate_access_token)):
    return "ok"
