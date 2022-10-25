from fastapi import FastAPI

from src.auth.services import *
from src.auth.routers import auth_router

app = FastAPI()
app.include_router(auth_router)


@app.get('/')
def index():
    get_user_by_email('23')
    return 'Hello, World!'
