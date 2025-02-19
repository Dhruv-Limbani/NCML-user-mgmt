# fastapi
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

# db
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
from db_service.mongodb_service import conn

# models and schemas
from models.user import User
from schemas.user import userEntity

# utilities
from utils.deps import get_current_user
from utils.utils import check_db_connection, get_hashed_password, verify_password, create_access_token, create_refresh_token


user_router = APIRouter()

@user_router.get('/me', summary='Get details of currently logged in user', tags=['user'])
async def get_me(user: User = Depends(get_current_user)):
    return user

@user_router.post("/signup", tags=["user"],
    responses = {
        201: {"description": "Signup Successful!"},
        400: {"description": "Bad Request!"},
        500: {"description": "Database Not Live!"}
    },
    description = "This endpoint creates a new user with the given details."
)
async def create_user(user: User):

    check_db_connection(conn)

    try:
        if conn.local.users.find_one({"email": user.email}):
            raise HTTPException(status_code=400, detail="User with this email already exists!")

        user.password = get_hashed_password(user.password)
        conn.local.users.insert_one(dict(user))
        return JSONResponse({"message": "User creation successful!"}, status_code=201)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@user_router.post('/login', tags=["user"],
    responses={
      201: {"description": "Login successful!"},
      401: {"description": "Invalid credentials"},
      500: {"description": "Database Not Live!"}
    },
    description="This endpoint creates access and refresh tokens for user."
)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):

    check_db_connection(conn)

    user = conn.local.users.find_one({"email": form_data.username})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = userEntity(user)
    hashed_pass = user['password']

    if not verify_password(form_data.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": create_access_token(user['email']),
        "refresh_token": create_refresh_token(user['email']),
        "token_type": "bearer"
    }

@user_router.put("/", tags=["user"],
    responses={
        200: {"description": "User modification successful!"},
        400: {"description": "Invalid user data!"},
        404: {"description": "User not found!"},
        409: {"description": "Email already in use!"},
        500: {"description": "Database Not Live!"}
    },
    description="This endpoint modifies the details of an existing user."
)
async def update_user(new: User, user: User = Depends(get_current_user)):

    check_db_connection(conn)

    try:
        new.password = get_hashed_password(new.password)
        updated_user = conn.local.users.find_one_and_update(
            {"email": user.email},
            {'$set': dict(new)},
            return_document=ReturnDocument.AFTER  # Return the updated user
        )

        if not updated_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return JSONResponse({"message": "User updated successfully", "updated details": userEntity(updated_user)}, status_code=200)

    except DuplicateKeyError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

from fastapi import Depends, HTTPException, status

@user_router.delete("/", tags=["user"],
    responses={
        204: {"description": "User deletion successful!"},
        404: {"description": "User not found!"},
        500: {"description": "Database Not Live!"}
    },
    description="This endpoint deletes a user by their email"
)
async def delete_user(user: User = Depends(get_current_user)):

    check_db_connection(conn)

    deleted_user = conn.local.users.find_one_and_delete({"email": user.email})

    if not deleted_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return {"message": "User deleted successfully"}