from sqlalchemy import Column, Integer, String, Text, ForeignKey
from database.db import Base


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)

    course_id = Column(
        Integer,
        ForeignKey("courses.id"),
        nullable=False
    )