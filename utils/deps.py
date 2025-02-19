# fastapi
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# db
from db_service.mongodb_service import conn

# models and schemas
from models.user import User
from models.token import TokenPayload
from schemas.user import userEntity

# utilities
from .utils import ALGORITHM, SECRET_KEY

# other
from datetime import datetime
from jose import jwt
from pydantic import ValidationError



reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="/user/login",
    scheme_name="JWT"
)

async def get_current_user(token: str = Depends(reuseable_oauth))->User:
    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_data = TokenPayload(**payload)

        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except(jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = conn.local.users.find_one({"email": token_data.sub})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )
    user = userEntity(user)
    return User(**user)