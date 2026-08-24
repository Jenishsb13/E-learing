from pydantic import BaseModel


class LessonCreate(BaseModel):
    title: str
    content: str