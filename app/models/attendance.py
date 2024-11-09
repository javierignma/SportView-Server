from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date as Date

class Attendance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    instructor_id: int = Field(foreign_key="user.id")
    student_id: int = Field(foreign_key="student.id")
    date: Date = Field(index=True)
    present: bool