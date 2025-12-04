from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
import requests
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .database import Base, engine, get_db
from .config import settings
from . import models, schemas, crud
from .utils import generate_short_code
from .auth import get_current_user

Base.metadata.create_all(bind=engine)
app = FastAPI(title="URL Shortener")

TOKEN_URL = f"{settings.KEYCLOAK_ISSUER}/protocol/openid-connect/token"

@app.post("/login", response_model=schemas.LoginResponse)
def login(body: schemas.LoginRequest):
    data = {
        "grant_type": "password",
        "client_id": settings.KEYCLOAK_CLIENT_ID,
        "username": body.username,
        "password": body.password,
    }
    try:
        r = requests.post(TOKEN_URL, data=data, timeout=10)
    except requests.RequestException:
        raise HTTPException(status_code=502, detail="Could not reach Keycloak")
    if r.status_code != 200:
        try:
            err = r.json().get("error_description") or r.text
        except Exception:
            err = r.text
        raise HTTPException(status_code=401, detail=err)

    j = r.json()
    return schemas.LoginResponse(
        access_token=j["access_token"],
        refresh_token=j["refresh_token"],
        token_type=j.get("token_type", "Bearer"),
        expires_in=j.get("expires_in", 300),
        refresh_expires_in=j.get("refresh_expires_in", 1800),
    )

@app.post("/shorten", response_model=schemas.ShortenResponse)
def shorten_url(req: schemas.ShortenRequest,
                db: Session = Depends(get_db),
                current_user: dict = Depends(get_current_user)):
    owner_sub = current_user["sub"]
     # Check if this URL already exists for this user
    existing = (
        db.query(models.ShortURL)
        .filter(
            models.ShortURL.owner_sub == owner_sub,
            models.ShortURL.original_url == str(req.url)
        )
        .first()
    )

    if existing:
        # Return SAME short URL instead of creating a new one
        return schemas.ShortenResponse(
            short_code=existing.short_code,
            short_url=f"{settings.SERVICE_BASE_URL.rstrip('/')}/{existing.short_code}"
        )

    # Otherwise generate a new unique code
    try:
        code = generate_short_code(16)
        obj = crud.create_short_url(db, owner_sub=owner_sub, original_url=str(req.url), short_code=code)
        return schemas.ShortenResponse(
            short_code=obj.short_code,
            short_url=f"{settings.SERVICE_BASE_URL.rstrip('/')}/{obj.short_code}"
        )
    except IntegrityError:
        db.rollback()
    raise HTTPException(status_code=500, detail="Could not generate unique short code")

@app.get("/urls", response_model=list[schemas.URLItem])
def list_urls(db: Session = Depends(get_db),
              current_user: dict = Depends(get_current_user)):
    return crud.list_user_urls(db, owner_sub=current_user["sub"])

@app.delete("/urls/{id}", status_code=204)
def delete_url(id: int,
               db: Session = Depends(get_db),
               current_user: dict = Depends(get_current_user)):
    obj = crud.get_url_by_id(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="URL not found")
    if obj.owner_sub != current_user["sub"]:
        raise HTTPException(status_code=403, detail="Not allowed to delete this URL")
    crud.delete_url(db, obj)
    return None

@app.get("/{short_code}")   
def redirect_short(short_code: str, db: Session = Depends(get_db)):
    obj = crud.get_by_short_code(db, short_code)
    if not obj:
        raise HTTPException(status_code=404, detail="Short code not found")
    crud.increment_clicks(db, obj)
    return RedirectResponse(url=obj.original_url)
