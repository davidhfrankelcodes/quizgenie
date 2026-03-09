from typing import Optional
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from auth import hash_password, require_admin, verify_password
from database import get_db
from models import User
from app_templates import render

router = APIRouter()


@router.get("/users")
async def list_users(
    request: Request,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    users = db.query(User).order_by(User.created_at).all()
    admin_user = db.query(User).filter(User.username == "admin").first()
    default_pw_warning = bool(admin_user and verify_password("changeme", admin_user.password_hash))
    return render(request, "admin/users.html", {
        "users": users,
        "default_pw_warning": default_pw_warning,
    }, current_user=admin)


@router.get("/users/new")
async def create_user_get(request: Request, admin: User = Depends(require_admin)):
    return render(request, "admin/create_user.html", {}, current_user=admin)


@router.post("/users/new")
async def create_user_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    is_admin: Optional[str] = Form(default=None),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    username = username.strip()
    if not username:
        return render(request, "admin/create_user.html",
                      {"error": "Username is required."}, current_user=admin)
    if len(password) < 8:
        return render(request, "admin/create_user.html",
                      {"error": "Password must be at least 8 characters."}, current_user=admin)
    if db.query(User).filter(User.username == username).first():
        return render(request, "admin/create_user.html",
                      {"error": f"Username '{username}' is already taken."}, current_user=admin)

    new_user = User(
        username=username,
        password_hash=hash_password(password),
        is_admin=is_admin is not None,
    )
    db.add(new_user)
    db.commit()
    return RedirectResponse("/admin/users?msg=created", status_code=302)
