from fastapi import APIRouter

from src.api.handlers import authentication

router = APIRouter()
router.include_router(authentication.router, tags=['authentication'], prefix='/auth')
