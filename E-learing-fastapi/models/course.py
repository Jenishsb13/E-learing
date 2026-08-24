from sqlalchemy import Column, Integer, String, Text, ForeignKey
from database.db import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    instructor_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )