# from fastapi import APIRouter, Depends, HTTPException, Query
# from sqlalchemy.orm import Session
# from app.database import SessionLocal
# from app.models.admin import Admin
# from app.models.food import Food
# from app.models.user import User
# from app.schemas.food import FoodCreate
# from app.core.security import hash_password
# from app.core.deps import get_current_admin

# router = APIRouter(prefix="/admin", tags=["Admin"])


# # =========================
# # DATABASE DEPENDENCY
# # =========================
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# # =========================
# # CREATE ADMIN (ONE TIME)
# # =========================
# @router.post("/create")
# def create_admin(email: str, password: str, db: Session = Depends(get_db)):
#     existing = db.query(Admin).filter(Admin.email == email).first()
#     if existing:
#         raise HTTPException(status_code=400, detail="Admin already exists")

#     admin = Admin(
#         email=email,
#         password=hash_password(password)
#     )
#     db.add(admin)
#     db.commit()
#     return {"message": "Admin created successfully"}


# # =========================
# # ADD FOOD
# # =========================
# @router.post("/food", dependencies=[Depends(get_current_admin)])
# def add_food(food: FoodCreate, db: Session = Depends(get_db)):
#     new_food = Food(**food.dict())
#     db.add(new_food)
#     db.commit()
#     db.refresh(new_food)
#     return {"message": "Food added successfully"}


# # =========================
# # LIST FOODS (PAGINATION + SEARCH)
# # =========================
# @router.get("/foods", dependencies=[Depends(get_current_admin)])
# def list_foods(
#     page: int = Query(1, ge=1),
#     limit: int = Query(10, ge=1, le=50),
#     search: str | None = None,
#     db: Session = Depends(get_db),
# ):
#     query = db.query(Food)

#     # 🔍 SEARCH BY NAME
#     if search:
#         query = query.filter(Food.name.ilike(f"%{search}%"))

#     foods = (
#         query
#         .offset((page - 1) * limit)
#         .limit(limit)
#         .all()
#     )

#     return foods


# # =========================
# # UPDATE FOOD
# # =========================
# @router.put("/food/{food_id}", dependencies=[Depends(get_current_admin)])
# def update_food(food_id: int, food: FoodCreate, db: Session = Depends(get_db)):
#     existing_food = db.query(Food).filter(Food.id == food_id).first()

#     if not existing_food:
#         raise HTTPException(status_code=404, detail="Food not found")

#     existing_food.name = food.name
#     existing_food.price = food.price
#     existing_food.description = food.description
#     existing_food.image_url = food.image_url

#     db.commit()
#     db.refresh(existing_food)

#     return {"message": "Food updated successfully"}


# # =========================
# # DELETE FOOD
# # =========================
# @router.delete("/food/{food_id}", dependencies=[Depends(get_current_admin)])
# def delete_food(food_id: int, db: Session = Depends(get_db)):
#     food = db.query(Food).filter(Food.id == food_id).first()

#     if not food:
#         raise HTTPException(status_code=404, detail="Food not found")

#     db.delete(food)
#     db.commit()
#     return {"message": "Food deleted successfully"}


# # =========================
# # LIST USERS
# # =========================
# @router.get("/users", dependencies=[Depends(get_current_admin)])
# def list_users(db: Session = Depends(get_db)):
#     return db.query(User).all()
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.admin import Admin
from app.models.food import Food
from app.models.user import User
from app.schemas.food import FoodCreate
from app.core.security import hash_password
from app.core.deps import get_current_admin
import uuid
import shutil
import os

router = APIRouter(prefix="/admin", tags=["Admin"])

UPLOAD_DIR = "app/static/uploads"

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
# CREATE ADMIN
# =========================
@router.post("/create")
def create_admin(email: str, password: str, db: Session = Depends(get_db)):
    if db.query(Admin).filter(Admin.email == email).first():
        raise HTTPException(status_code=400, detail="Admin already exists")

    admin = Admin(email=email, password=hash_password(password))
    db.add(admin)
    db.commit()
    return {"message": "Admin created"}

# =========================
# IMAGE UPLOAD
# =========================
@router.post("/upload", dependencies=[Depends(get_current_admin)])
def upload_image(file: UploadFile = File(...)):
    if file.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Invalid image type")

    filename = f"{uuid.uuid4()}_{file.filename}"
    path = os.path.join(UPLOAD_DIR, filename)

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "image_url": f"http://127.0.0.1:8000/static/uploads/{filename}"
    }

# =========================
# ADD FOOD
# =========================
@router.post("/food", dependencies=[Depends(get_current_admin)])
def add_food(food: FoodCreate, db: Session = Depends(get_db)):
    if not food.name or food.price <= 0:
        raise HTTPException(status_code=400, detail="Invalid food data")

    new_food = Food(**food.dict())
    db.add(new_food)
    db.commit()
    db.refresh(new_food)
    return new_food

# =========================
# LIST FOODS (PAGINATION + SEARCH)
# =========================
@router.get("/foods", dependencies=[Depends(get_current_admin)])
def list_foods(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    search: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Food)
    if search:
        query = query.filter(Food.name.ilike(f"%{search}%"))

    return query.offset((page - 1) * limit).limit(limit).all()

# =========================
# UPDATE FOOD
# =========================
@router.put("/food/{food_id}", dependencies=[Depends(get_current_admin)])
def update_food(food_id: int, food: FoodCreate, db: Session = Depends(get_db)):
    item = db.query(Food).filter(Food.id == food_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Food not found")

    item.name = food.name
    item.description = food.description
    item.price = food.price
    item.image_url = food.image_url

    db.commit()
    db.refresh(item)
    return item

# =========================
# DELETE FOOD
# =========================
@router.delete("/food/{food_id}", dependencies=[Depends(get_current_admin)])
def delete_food(food_id: int, db: Session = Depends(get_db)):
    item = db.query(Food).filter(Food.id == food_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Food not found")

    db.delete(item)
    db.commit()
    return {"message": "Food deleted"}

@router.get("/users", dependencies=[Depends(get_current_admin)])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()

