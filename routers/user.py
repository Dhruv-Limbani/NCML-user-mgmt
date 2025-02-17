from fastapi import APIRouter

from models.user import User
from db_service.mongodb_service import conn
from schemas.user import userEntity
from fastapi.responses import JSONResponse
from bson import ObjectId
user_router = APIRouter()

@user_router.get("/{id}", tags=["user"],
    responses = {
        200: {"description": "User fetched successfully"},
        404: {"description": "User does not exist"},
        422: {"description": "Invalid Id passed"},
    },
    description = "This endpoint fetches the user details using Id."
)
async def get_user(id):
    try:
        result = conn.local.users.find_one({"_id": ObjectId(id)})
        if result is not None:
            return JSONResponse(userEntity(result), status_code=200)
        else:
            return JSONResponse({"message": "User not found"}, status_code=404)
    except Exception as e:
        return JSONResponse({"message": "Invalid Id"}, status_code=422)

@user_router.post("/", tags=["user"],
    responses = {
        201: {"description": "User creation successful"},
        400: {"description": "Corrupt user object passed"}
    },
    description = "This endpoint creates a new user with the given details."
)
async def create_user(user: User):
    try:
        conn.local.users.insert_one(dict(user))
        return JSONResponse({"message": "User created successfully"}, status_code=201)
    except Exception as e:
        return JSONResponse({"message": str(e)}, status_code=400)


@user_router.put("/{id}", tags=["user"],
    responses={
        200: {"description": "User modification successful"},
        400: {"description": "Corrupt user object passed"},
        404: {"description": "User does not exist"}
    },
    description="This endpoint modifies the details of an existing user."
)
async def update_user(id, user: User):
    try:
        result = conn.local.users.find_one_and_update({"_id": ObjectId(id)}, {'$set': dict(user)})
        if result is not None:
            result = conn.local.users.find_one({"_id": ObjectId(id)})
            return JSONResponse({"message": "User updated successfully", "updated details": userEntity(result)}, status_code=200)
        else:
            return JSONResponse({"message": "User not found"}, status_code=404)
    except Exception as e:
        return JSONResponse({"message": "Invalid Id"}, status_code=400)

@user_router.delete("/{id}", tags=["user"],
    responses={
        200: {"description": "User deleted successfully"},
        404: {"description": "User does not exist"},
        422: {"description": "Invalid Id passed"}
    },
    description="This endpoint deletes a user by their Id"
)
async def delete_user(id):
    try:
        result = conn.local.users.find_one_and_delete({"_id": ObjectId(id)})
        if result is not None:
            return JSONResponse({"message": "User deleted successfully"}, status_code=201)
        else:
            return JSONResponse({"message": "User not found"}, status_code=404)
    except Exception as e:
        return JSONResponse({"message": "Invalid Id"}, status_code=400)