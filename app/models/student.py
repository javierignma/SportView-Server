from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date

class Student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    instructor_id: int = Field(foreign_key="user.id")
    name: str
    email: str
    rut: str
    age: Optional[int]
    weight: Optional[float]
    height: Optional[float]

class StudentProgress(SQLModel, table=True):
    student_id: int = Field(foreign_key="student.id", primary_key=True)
    progress_date: date = Field(primary_key=True)
    technique: Optional[int]
    physique: Optional[int]
    combat_iq: Optional[int]