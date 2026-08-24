from pydantic import BaseModel, EmailStr
from enum import Enum


class UserRole(str, Enum):
    instructor = "instructor"
    student = "student"


class Register(BaseModel):
    name: str
    email: EmailStr
    phone: str
    password: str
    role: UserRole
    
    
class Login(BaseModel):
    email: EmailStr
    password: str