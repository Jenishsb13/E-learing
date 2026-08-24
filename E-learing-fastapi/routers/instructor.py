from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_db
from dependencies.auth import get_current_user
from models.course import Course
from schemas.course import CourseCreate

from sqlalchemy import select

from models.course import Course
from models.lesson import Lesson
from schemas.lesson import LessonCreate
from schemas.course import CourseCreate, CourseUpdate


router = APIRouter(
    prefix="/instructor",
    tags=["Instructor"]
)


@router.get("/dashboard")
async def instructor_dashboard(
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "instructor":
        raise HTTPException(
            status_code=403,
            detail="Instructor access only"
        )

    return {
        "message": "Welcome to Instructor Dashboard",
        "user_id": current_user["user_id"],
        "email": current_user["email"],
        "role": current_user["role"]
    }


@router.post("/course")
async def create_course(
    course: CourseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Only instructor can create course
    if current_user["role"] != "instructor":
        raise HTTPException(
            status_code=403,
            detail="Instructor access only"
        )

    new_course = Course(
        title=course.title,
        description=course.description,
        instructor_id=current_user["user_id"]
    )

    db.add(new_course)

    await db.commit()
    await db.refresh(new_course)

    return {
        "message": "Course created successfully",
        "course_id": new_course.id,
        "title": new_course.title,
        "description": new_course.description,
        "instructor_id": new_course.instructor_id
    }
    
@router.post("/course/{course_id}/lesson")
async def add_lesson(
    course_id: int,
    lesson: LessonCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Only instructor can add lessons
    if current_user["role"] != "instructor":
        raise HTTPException(
            status_code=403,
            detail="Instructor access only"
        )

    # Check course
    result = await db.execute(
        select(Course).where(Course.id == course_id)
    )

    course = result.scalar_one_or_none()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    # Check course belongs to instructor
    if course.instructor_id != current_user["user_id"]:
        raise HTTPException(
            status_code=403,
            detail="You can only add lessons to your own course"
        )

    # Create lesson
    new_lesson = Lesson(
        title=lesson.title,
        content=lesson.content,
        course_id=course_id
    )

    db.add(new_lesson)

    await db.commit()
    await db.refresh(new_lesson)

    return {
        "message": "Lesson added successfully",
        "lesson_id": new_lesson.id,
        "title": new_lesson.title,
        "content": new_lesson.content,
        "course_id": new_lesson.course_id
    }
    
    # =========================
# VIEW MY COURSES
# =========================

@router.get("/courses")
async def my_courses(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "instructor":
        raise HTTPException(
            status_code=403,
            detail="Instructor access only"
        )

    result = await db.execute(
        select(Course).where(
            Course.instructor_id == current_user["user_id"]
        )
    )

    courses = result.scalars().all()

    return {
        "message": "Courses fetched successfully",
        "courses": [
            {
                "id": course.id,
                "title": course.title,
                "description": course.description
            }
            for course in courses
        ]
    }
    
    # =========================
# UPDATE COURSE
# =========================

@router.put("/course/{course_id}")
async def update_course(
    course_id: int,
    course_data: CourseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "instructor":
        raise HTTPException(
            status_code=403,
            detail="Instructor access only"
        )

    result = await db.execute(
        select(Course).where(
            Course.id == course_id
        )
    )

    course = result.scalar_one_or_none()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if course.instructor_id != current_user["user_id"]:
        raise HTTPException(
            status_code=403,
            detail="You can only update your own course"
        )

    course.title = course_data.title
    course.description = course_data.description

    await db.commit()
    await db.refresh(course)

    return {
        "message": "Course updated successfully",
        "course_id": course.id,
        "title": course.title,
        "description": course.description
    }
    
    # =========================
# DELETE COURSE
# =========================

@router.delete("/course/{course_id}")
async def delete_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "instructor":
        raise HTTPException(
            status_code=403,
            detail="Instructor access only"
        )

    result = await db.execute(
        select(Course).where(
            Course.id == course_id
        )
    )

    course = result.scalar_one_or_none()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if course.instructor_id != current_user["user_id"]:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own course"
        )

    await db.delete(course)
    await db.commit()

    return {
        "message": "Course deleted successfully",
        "course_id": course_id
    }