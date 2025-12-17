from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.models import user as user_model, admin as admin_model, food

from app.routes.auth import router as auth_router
from app.routes.admin import router as admin_router
from app.user import router as user_router   # ✅ FIXED IMPORT

app = FastAPI(title="StackFood Clone API")

# ================= ROUTERS =================
app.include_router(auth_router)     # /auth/login
app.include_router(admin_router)    # /admin/foods
app.include_router(user_router)     # /foods , /orders

# ================= DATABASE =================
@app.on_event("startup")
def startup():
    user_model.Base.metadata.create_all(bind=engine)
    admin_model.Base.metadata.create_all(bind=engine)
    food.Base.metadata.create_all(bind=engine)

# ================= CORS =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://stackfoodadmin.netlify.app" ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Backend is running 🚀"}
