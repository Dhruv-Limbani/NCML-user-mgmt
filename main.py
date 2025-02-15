import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.user import user_router
from routers.health import health_router

app = FastAPI()

app.include_router(user_router, prefix="/user")
app.include_router(health_router, prefix="/health")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)