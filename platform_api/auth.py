from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt

from .config import Settings, get_settings
from .schemas import Actor


bearer = HTTPBearer(auto_error=False)


def current_actor(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), settings: Settings = Depends(get_settings)) -> Actor:
    if settings.auth_mode == "disabled" and settings.environment != "production":
        return Actor(subject="local-development", roles=("platform-admin",))
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="bearer token required")
    try:
        claims = jwt.decode(
            credentials.credentials,
            settings.oidc_public_key,
            algorithms=["RS256"],
            audience=settings.oidc_audience,
            issuer=settings.oidc_issuer,
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid bearer token") from exc
    raw_roles = claims.get("roles", [])
    roles = (raw_roles,) if isinstance(raw_roles, str) else tuple(raw_roles)
    if not set(roles).intersection(settings.allowed_roles.split(",")):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="platform role required")
    return Actor(subject=claims["sub"], roles=roles)
