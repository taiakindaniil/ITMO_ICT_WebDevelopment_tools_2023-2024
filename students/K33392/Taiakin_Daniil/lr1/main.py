from contextlib import asynccontextmanager
from fastapi import FastAPI

from routers import auth_router, users_router, books_router, tags_router, boxes_router, crossings_router

from database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(books_router)
app.include_router(tags_router)
app.include_router(boxes_router)
app.include_router(crossings_router)