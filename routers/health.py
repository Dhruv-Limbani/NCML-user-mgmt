# fastapi
from fastapi import APIRouter

# db
from db_service.mongodb_service import conn

# models and schemas
from schemas.user import usersEntity

# utilities
from utils.utils import check_db_connection

health_router = APIRouter()

@health_router.get("/", tags=["health"], response_model=dict,
    responses={
       500: {"description": "Database Not Live!"}
    },
   description="Health check for the database."
)
async def health_check():
    """Checks database connection and returns a list of users if the DB is live."""
    check_db_connection(conn)
    users = list(conn.local.users.find())

    return {"status": "Database is live", "users": usersEntity(users)}
