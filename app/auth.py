import time, requests
from typing import Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from .config import settings

security = HTTPBearer()
_JWKS: Dict[str, Any] | None = None
_FETCHED_AT = 0
_TTL = 60 * 60

def _jwks() -> Dict[str, Any]:
    global _JWKS, _FETCHED_AT
    if not _JWKS or (time.time() - _FETCHED_AT) > _TTL:
        url = f"{settings.KEYCLOAK_ISSUER}/protocol/openid-connect/certs"
        r = requests.get(url, timeout=5); r.raise_for_status()
        _JWKS = r.json(); _FETCHED_AT = time.time()
    return _JWKS

def _verify(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(
            token,
            _jwks(),
            algorithms=["RS256", "PS256", "ES256"],
            issuer=settings.KEYCLOAK_ISSUER,
            audience=settings.KEYCLOAK_CLIENT_ID,
            options={"verify_aud": not settings.DISABLE_AUDIENCE_CHECK},
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTClaimsError as e:
        raise HTTPException(status_code=401, detail=f"Invalid claims: {e}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {e}")

def _require_user_role(claims: Dict[str, Any]) -> None:
    roles = []
    ra = claims.get("realm_access") or {}
    if isinstance(ra, dict):
        roles += ra.get("roles") or []
    res = claims.get("resource_access") or {}
    if isinstance(res, dict):
        for _, info in res.items():
            if isinstance(info, dict):
                roles += info.get("roles") or []
    if "user" not in roles:
        raise HTTPException(status_code=401, detail="Required role 'user' missing")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    claims = _verify(credentials.credentials)
    _require_user_role(claims)
    sub = claims.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Missing 'sub' in token")
    return {"sub": sub, "claims": claims}
