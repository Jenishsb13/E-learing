from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.db import get_db
from dependencies.auth import get_current_user
from models.course import Course
from models.lesson import Lesson

from models.enrollment import Enrollment
from models.progress import Progress




router = APIRouter(
    prefix="/student",
    tags=["Student"]
)


# =========================
# STUDENT DASHBOARD
# =========================

@router.get("/dashboard")
async def student_dashboard(
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "student":
        raise HTTPException(
            status_code=403,
            detail="Student access only"
        )

    return {
        "message": "Welcome to Student Dashboard",
        "user_id": current_user["user_id"],
        "email": current_user["email"],
        "role": current_user["role"]
    }


# =========================
# VIEW ALL COURSES
# =========================

@router.get("/courses")
async def view_courses(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Only student can view this API
    if current_user["role"] != "student":
        raise HTTPException(
            status_code=403,
            detail="Student access only"
        )

    result = await db.execute(
        select(Course)
    )

    courses = result.scalars().all()

    return {
        "message": "Courses fetched successfully",
        "courses": [
            {
                "id": course.id,
                "title": course.title,
                "description": course.description,
                "instructor_id": course.instructor_id
            }
            for course in courses
        ]
    }
    
    # =========================
# VIEW COURSE LESSONS
# =========================

@router.get("/courses/{course_id}/lessons")
async def view_lessons(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Only student can access
    if current_user["role"] != "student":
        raise HTTPException(
            status_code=403,
            detail="Student access only"
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

    # Get lessons
    result = await db.execute(
        select(Lesson).where(
            Lesson.course_id == course_id
        )
    )

    lessons = result.scalars().all()

    return {
        "course_id": course.id,
        "course_title": course.title,
        "lessons": [
            {
                "id": lesson.id,
                "title": lesson.title,
                "content": lesson.content
            }
            for lesson in lessons
        ]
    }
    
    # =========================
# ENROLL IN COURSE
# =========================

@router.post("/courses/{course_id}/enroll")
async def enroll_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Only student can enroll
    if current_user["role"] != "student":
        raise HTTPException(
            status_code=403,
            detail="Student access only"
        )

    student_id = current_user["user_id"]

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

    # Check existing enrollment
    result = await db.execute(
        select(Enrollment).where(
            Enrollment.student_id == student_id,
            Enrollment.course_id == course_id
        )
    )

    existing_enrollment = result.scalar_one_or_none()

    if existing_enrollment:
        raise HTTPException(
            status_code=400,
            detail="Already enrolled in this course"
        )

    # Create enrollment
    enrollment = Enrollment(
        student_id=student_id,
        course_id=course_id
    )

    db.add(enrollment)

    await db.commit()
    await db.refresh(enrollment)

    return {
        "message": "Enrolled successfully",
        "enrollment_id": enrollment.id,
        "student_id": enrollment.student_id,
        "course_id": enrollment.course_id,
        "course_title": course.title
    }
    
    # =========================
# MY ENROLLED COURSES
# =========================

@router.get("/my-courses")
async def my_courses(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Only student can access
    if current_user["role"] != "student":
        raise HTTPException(
            status_code=403,
            detail="Student access only"
        )

    student_id = current_user["user_id"]

    # Get enrolled courses
    result = await db.execute(
        select(Enrollment, Course)
        .join(
            Course,
            Enrollment.course_id == Course.id
        )
        .where(
            Enrollment.student_id == student_id
        )
    )

    rows = result.all()

    return {
        "message": "Enrolled courses fetched successfully",
        "courses": [
            {
                "enrollment_id": enrollment.id,
                "course_id": course.id,
                "title": course.title,
                "description": course.description,
                "instructor_id": course.instructor_id
            }
            for enrollment, course in rows
        ]
    }
    
    # =========================
# MARK LESSON COMPLETED
# =========================

@router.post("/courses/{course_id}/lessons/{lesson_id}/complete")
async def complete_lesson(
    course_id: int,
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Only student
    if current_user["role"] != "student":
        raise HTTPException(
            status_code=403,
            detail="Student access only"
        )

    student_id = current_user["user_id"]

    # Check enrollment
    result = await db.execute(
        select(Enrollment).where(
            Enrollment.student_id == student_id,
            Enrollment.course_id == course_id
        )
    )

    enrollment = result.scalar_one_or_none()

    if enrollment is None:
        raise HTTPException(
            status_code=403,
            detail="You are not enrolled in this course"
        )

    # Check lesson
    result = await db.execute(
        select(Lesson).where(
            Lesson.id == lesson_id,
            Lesson.course_id == course_id
        )
    )

    lesson = result.scalar_one_or_none()

    if lesson is None:
        raise HTTPException(
            status_code=404,
            detail="Lesson not found"
        )

    # Check existing progress
    result = await db.execute(
        select(Progress).where(
            Progress.student_id == student_id,
            Progress.course_id == course_id,
            Progress.lesson_id == lesson_id
        )
    )

    progress = result.scalar_one_or_none()

    if progress:
        progress.completed = True
    else:
        progress = Progress(
            student_id=student_id,
            course_id=course_id,
            lesson_id=lesson_id,
            completed=True
        )

        db.add(progress)

    await db.commit()
    await db.refresh(progress)

    return {
        "message": "Lesson completed successfully",
        "student_id": student_id,
        "course_id": course_id,
        "lesson_id": lesson_id,
        "completed": progress.completed
    }
    
    # =========================
# VIEW COURSE PROGRESS
# =========================

@router.get("/courses/{course_id}/progress")
async def course_progress(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Only student
    if current_user["role"] != "student":
        raise HTTPException(
            status_code=403,
            detail="Student access only"
        )

    student_id = current_user["user_id"]

    # Check enrollment
    result = await db.execute(
        select(Enrollment).where(
            Enrollment.student_id == student_id,
            Enrollment.course_id == course_id
        )
    )

    enrollment = result.scalar_one_or_none()

    if enrollment is None:
        raise HTTPException(
            status_code=403,
            detail="You are not enrolled in this course"
        )

    # Get all lessons
    result = await db.execute(
        select(Lesson).where(
            Lesson.course_id == course_id
        )
    )

    lessons = result.scalars().all()

    total_lessons = len(lessons)

    # Get completed lessons
    result = await db.execute(
        select(Progress).where(
            Progress.student_id == student_id,
            Progress.course_id == course_id,
            Progress.completed == True
        )
    )

    completed_progress = result.scalars().all()

    completed_lessons = len(completed_progress)

    # Calculate percentage
    if total_lessons == 0:
        percentage = 0
    else:
        percentage = (
            completed_lessons / total_lessons
        ) * 100

    return {
        "course_id": course_id,
        "total_lessons": total_lessons,
        "completed_lessons": completed_lessons,
        "remaining_lessons": total_lessons - completed_lessons,
        "progress_percentage": round(percentage, 2)
    }