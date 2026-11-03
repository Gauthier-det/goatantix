from fastapi import APIRouter

from app.config import settings
from app.schemas import AuthRequest, AuthResult

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/verify", response_model=AuthResult)
def verify(req: AuthRequest):
    return AuthResult(ok=req.password == settings.admin_password)
