from pydantic import BaseModel, HttpUrl
from datetime import datetime

class ShortenRequest(BaseModel):
    url: HttpUrl

class ShortenResponse(BaseModel):
    short_code: str
    short_url: HttpUrl

class URLItem(BaseModel):
    id: int
    short_code: str
    original_url: HttpUrl
    clicks: int
    created_at: datetime

    model_config = {"from_attributes": True}

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    refresh_expires_in: int