import os
from dotenv import load_dotenv
from jose import jwt

from datetime import datetime, timedelta, timezone

load_dotenv()

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.environ["JWT_SECRET_KEY"], algorithm="HS256")
    return encoded_jwt