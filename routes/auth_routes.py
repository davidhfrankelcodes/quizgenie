from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from auth import COOKIE_NAME, create_session_cookie, get_current_user, hash_password, verify_password
from database import get_db
from models import User
from app_templates import render

router = APIRouter()


@router.get("/login")
async def login_get(request: Request):
    token = request.cookies.get(COOKIE_NAME)
    if token:
        return RedirectResponse("/", status_code=302)
    return render(request, "login.html", {})


@router.post("/login")
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        return render(request, "login.html", {"error": "Invalid username or password."})
    token = create_session_cookie(user.id)
    response = RedirectResponse("/", status_code=302)
    response.set_cookie(COOKIE_NAME, token, httponly=True, samesite="lax", max_age=86400)
    return response


@router.get("/logout")
async def logout():
    response = RedirectResponse("/login", status_code=302)
    response.delete_cookie(COOKIE_NAME)
    return response


@router.get("/change-password")
async def change_password_get(request: Request, user: User = Depends(get_current_user)):
    return render(request, "change_password.html", {}, current_user=user)


@router.post("/change-password")
async def change_password_post(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(current_password, user.password_hash):
        return render(request, "change_password.html",
                      {"error": "Current password is incorrect."}, current_user=user)
    if new_password != confirm_password:
        return render(request, "change_password.html",
                      {"error": "New passwords do not match."}, current_user=user)
    if len(new_password) < 8:
        return render(request, "change_password.html",
                      {"error": "New password must be at least 8 characters."}, current_user=user)

    user.password_hash = hash_password(new_password)
    db.commit()
    return RedirectResponse("/?msg=password_changed", status_code=302)
