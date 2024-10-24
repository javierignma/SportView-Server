from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date as Date

class Attendance(SQLModel, table=True):
    student_id: int = Field(foreign_key="student.id", primary_key=True)
    date: Date = Field(primary_key=True)
    present: Optional[bool]