from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.food import Food

router = APIRouter(tags=["User"])

# =========================
# DATABASE DEPENDENCY
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
# USER: LIST FOODS (PUBLIC)
# =========================
@router.get("/foods")
def get_foods(db: Session = Depends(get_db)):
    return db.query(Food).all()
