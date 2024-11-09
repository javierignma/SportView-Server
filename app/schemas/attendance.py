from sqlmodel import SQLModel
from typing import Optional
from datetime import date as Date

class AttendanceResponse(SQLModel, table=False):
    id: int
    instructor_id: int 
    student_id: int
    student_name: str
    date: Date
    present: bool