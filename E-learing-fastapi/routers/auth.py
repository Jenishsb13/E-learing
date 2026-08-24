# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select

# from database.db import get_db
# from models.user import User
# from schemas.auth import Register , Login

# router = APIRouter(prefix="/auth", tags=["Authentication"])


# @router.post("/register")
# async def register(
#     user: Register,
#     db: AsyncSession = Depends(get_db)
# ):
#     # Check email
#     result = await db.execute(
#         select(User).where(User.email == user.email)
#     )

#     existing_user = result.scalar_one_or_none()

#     if existing_user:
#         raise HTTPException(
#             status_code=400,
#             detail="Email already registered"
#         )

#     # Create user
#     new_user = User(
#         name=user.name,
#         email=user.email,
#         phone=user.phone,
#         password=user.password,
#         role=user.role
#     )

#     db.add(new_user)

#     await db.commit()
#     await db.refresh(new_user)

#     return {
#         "message": "Registration successful",
#         "user_id": new_user.id,
#         "name": new_user.name,
#         "email": new_user.email,
#         "role": new_user.role
#     }
    
#     # LOGIN
# @router.post("/login")
# async def login(
#     user: Login,
#     db: AsyncSession = Depends(get_db)
# ):
#     result = await db.execute(
#         select(User).where(User.email == user.email)
#     )

#     db_user = result.scalar_one_or_none()

#     # User not found
#     if db_user is None:
#         raise HTTPException(
#             status_code=404,
#             detail="User not found"
#         )

#     # Password check
#     if db_user.password != user.password:
#         raise HTTPException(
#             status_code=401,
#             detail="Incorrect password"
#         )

#     return {
#         "message": "Login successful",
#         "user_id": db_user.id,
#         "name": db_user.name,
#         "email": db_user.email,
#         "role": db_user.role
#     }

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.db import get_db
from models.user import User
from schemas.auth import Register, Login
from core.security import create_access_token   


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# =========================
# REGISTER
# =========================

@router.post("/register")
async def register(
    user: Register,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(User).where(User.email == user.email)
    )

    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        password=user.password,
        role=user.role
    )

    db.add(new_user)

    await db.commit()
    await db.refresh(new_user)

    return {
        "message": "Registration successful",
        "user_id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,
        "role": new_user.role
    }


# =========================
# LOGIN
# =========================

@router.post("/login")
async def login(
    user: Login,
    db: AsyncSession = Depends(get_db)
):
    # 1. Verify Email
    result = await db.execute(
        select(User).where(User.email == user.email)
    )

    db_user = result.scalar_one_or_none()

    if db_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # 2. Verify Password
    if db_user.password != user.password:
        raise HTTPException(
            status_code=401,
            detail="Incorrect password"
        )

    # 3. Check Role
    if db_user.role == "instructor":
        role = "instructor"

    elif db_user.role == "student":
        role = "student"

    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid user role"
        )

    # 4. Generate JWT
    access_token = create_access_token(
        data={
            "user_id": db_user.id,
            "email": db_user.email,
            "role": role
        }
    )

    # 5. Response
    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": db_user.id,
        "name": db_user.name,
        "email": db_user.email,
        "role": role
    }
    
    
