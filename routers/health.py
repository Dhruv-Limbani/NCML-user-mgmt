from fastapi import APIRouter
from db_service.mongodb_service import conn
from schemas.user import usersEntity

health_router = APIRouter()

@health_router.get("/", tags=["health"])
async def get_users():
    print(conn.local.user.find())
    print(usersEntity(conn.local.users.find()))
    return usersEntity(conn.local.users.find())