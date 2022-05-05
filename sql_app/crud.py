from sqlalchemy.orm import Session

from . import models, schemas


def get_apk_details(db: Session, apk_id: int):
    return db.query(models.APKDetails).filter(models.APKDetails.id == apk_id).first()

def get_first_apk_details(db: Session):
    return db.query(models.APKDetails).order_by(models.APKDetails.id.desc()).first()


def get_all_apk_details(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.APKDetails).offset(skip).limit(limit).all()


def create_apk_details_item(db: Session, item: schemas.APKDetailsCreate):
    db_item = models.APKDetails(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

