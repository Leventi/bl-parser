from fastapi import APIRouter
from . import monopoly

router = APIRouter()
router.include_router(monopoly.router)
