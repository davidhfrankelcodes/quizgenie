import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

from fastapi import Depends, FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from auth import NotAuthenticated, NotAuthorized, get_current_user, hash_password
from database import SessionLocal, create_tables, get_db
from models import Bucket, User
from app_templates import render
from routes.auth_routes import router as auth_router
from routes.admin_routes import router as admin_router
from routes.bucket_routes import router as bucket_router
from routes.quiz_routes import router as quiz_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs("data", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)
    create_tables()
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            admin = User(
                username="admin",
                password_hash=hash_password("changeme"),
                is_admin=True,
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()
    yield


app = FastAPI(title="QuizGenie", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router)
app.include_router(admin_router, prefix="/admin")
app.include_router(bucket_router, prefix="/buckets")
app.include_router(quiz_router, prefix="/quizzes")


@app.exception_handler(NotAuthenticated)
async def not_authenticated_handler(request: Request, exc: NotAuthenticated):
    return RedirectResponse("/login", status_code=303)


@app.exception_handler(NotAuthorized)
async def not_authorized_handler(request: Request, exc: NotAuthorized):
    return RedirectResponse("/?msg=forbidden", status_code=303)


@app.get("/")
async def root():
    return RedirectResponse("/dashboard", status_code=302)


@app.get("/dashboard")
async def dashboard(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    buckets = db.query(Bucket).order_by(Bucket.created_at.desc()).all()
    return render(request, "dashboard.html", {"buckets": buckets}, current_user=user)
