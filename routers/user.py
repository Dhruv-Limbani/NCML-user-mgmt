from fastapi import APIRouter

from models.user import User
from db_service.mongodb_service import conn
from schemas.user import usersEntity
user_router = APIRouter()

@user_router.get("/", tags=["user"])
async def get_user():
    return usersEntity(conn.local.users.find())

@user_router.post("/", tags=["user"])
async def create_user(user: User):
    conn.local.users.insert_one(dict(user))
    return usersEntity(conn.local.users.find())