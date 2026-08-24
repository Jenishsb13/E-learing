from pydantic import BaseModel


class CourseCreate(BaseModel):
    title: str
    description: str


class CourseUpdate(BaseModel):
    title: str
    description: str