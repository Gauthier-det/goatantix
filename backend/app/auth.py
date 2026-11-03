from fastapi import Header, HTTPException

from app.config import settings


def require_admin(x_admin_password: str | None = Header(default=None)) -> None:
    if not x_admin_password or x_admin_password != settings.admin_password:
        raise HTTPException(status_code=401, detail="Mot de passe invalide")
