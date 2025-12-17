from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.models.admin import Admin
from app.schemas.user import UserSignup, UserLogin
from app.schemas.admin import AdminLogin
from app.core.security import hash_password, verify_password
from app.core.jwt import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/signup")
def signup(data: UserSignup, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    user = User(
        name=data.name,
        email=data.email,
        password=hash_password(data.password)
    )
    db.add(user)
    db.commit()
    return {"message": "User registered successfully"}

@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"user_id": user.id})
    return {"access_token": token}

@router.post("/admin/login")
def admin_login(data: AdminLogin, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.email == data.email).first()

    if not admin or not verify_password(data.password, admin.password):
        raise HTTPException(status_code=401, detail="Invalid admin credentials")

    token = create_access_token({"sub": admin.email,
    "admin_id": admin.id,
    "role": "admin"})
    return {"access_token": token}

@router.post("/admin/login")
def admin_login(data: AdminLogin, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.email == data.email).first()

    if not admin or not verify_password(data.password, admin.password):
        raise HTTPException(status_code=401, detail="Invalid admin credentials")

    token = create_access_token({
        "sub": admin.email,
        "admin_id": admin.id,
        "role": "admin"
    })

    return {"access_token": token}
