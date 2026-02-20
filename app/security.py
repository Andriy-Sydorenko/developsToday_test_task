import datetime

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security.utils import get_authorization_scheme_param

from app.config import settings
from app.constants import JWT_TOKEN_COOKIE_KEY


pwd_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return pwd_hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return pwd_hasher.verify(password_hash, password)
    except VerifyMismatchError, VerificationError, InvalidHashError:
        return False


def create_access_token(user_id: str) -> str:
    expires_at = datetime.datetime.now(datetime.UTC) + datetime.timedelta(
        minutes=settings.jwt_access_token_expire_minutes,
    )
    payload = {"sub": user_id, "exp": expires_at}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def get_access_token(
    request: Request,
    authorization: str | None = Header(default=None),
) -> str:
    cookie_token = request.cookies.get(JWT_TOKEN_COOKIE_KEY)
    if cookie_token:
        return cookie_token

    scheme, param = get_authorization_scheme_param(authorization)
    if scheme.lower() == "bearer" and param:
        return param

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")


def get_current_user_id(token: str = Depends(get_access_token)) -> str:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id: str = payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired") from None
    except jwt.InvalidTokenError, KeyError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from None
    return user_id
