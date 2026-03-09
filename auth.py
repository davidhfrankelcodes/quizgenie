import os
import bcrypt
from itsdangerous import TimestampSigner, SignatureExpired, BadSignature
from fastapi import Depends, Request
from sqlalchemy.orm import Session
from database import get_db

COOKIE_NAME = "qg_session"
SESSION_MAX_AGE = 86400  # 24 hours


def _get_signer() -> TimestampSigner:
    secret = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    return TimestampSigner(secret)


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_session_cookie(user_id: int) -> str:
    return _get_signer().sign(str(user_id)).decode()


def read_session_cookie(token: str) -> int | None:
    try:
        value = _get_signer().unsign(token, max_age=SESSION_MAX_AGE)
        return int(value)
    except (SignatureExpired, BadSignature, ValueError):
        return None


class NotAuthenticated(Exception):
    pass


class NotAuthorized(Exception):
    pass


def get_current_user(request: Request, db: Session = Depends(get_db)):
    from models import User
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise NotAuthenticated()
    user_id = read_session_cookie(token)
    if user_id is None:
        raise NotAuthenticated()
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise NotAuthenticated()
    return user


def require_admin(user=Depends(get_current_user)):
    if not user.is_admin:
        raise NotAuthorized()
    return user
