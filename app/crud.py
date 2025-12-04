from sqlalchemy.orm import Session
from typing import Optional, List
from . import models

def create_short_url(db: Session, owner_sub: str, original_url: str, short_code: str) -> models.ShortURL:
    obj = models.ShortURL(owner_sub=owner_sub, original_url=original_url, short_code=short_code)
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

def get_by_short_code(db: Session, short_code: str) -> Optional[models.ShortURL]:
    return db.query(models.ShortURL).filter(models.ShortURL.short_code == short_code).first()

def increment_clicks(db: Session, obj: models.ShortURL):
    obj.clicks = (obj.clicks or 0) + 1
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

def list_user_urls(db: Session, owner_sub: str) -> List[models.ShortURL]:
    return (db.query(models.ShortURL)
            .filter(models.ShortURL.owner_sub == owner_sub)
            .order_by(models.ShortURL.created_at.desc())
            .all())

def get_url_by_id(db: Session, id: int) -> Optional[models.ShortURL]:
    return db.query(models.ShortURL).filter(models.ShortURL.id == id).first()

def delete_url(db: Session, obj: models.ShortURL):
    db.delete(obj); db.commit()
