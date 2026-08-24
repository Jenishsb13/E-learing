from fastapi import FastAPI

from database.db import engine, Base
from models.user import User
from routers.auth import router as auth_router

from routers.instructor import router as instructor_router
from routers.student import router as student_router
from models.course import Course
from models.lesson import Lesson
from models.enrollment import Enrollment
from models.progress import Progress


app = FastAPI(
    title="E-Learning API"
)


@app.on_event("startup")
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(auth_router)
app.include_router(instructor_router)
app.include_router(student_router)


@app.get("/")
async def home():
    return {
        "message": "E-Learning API is running"
    }
    
    