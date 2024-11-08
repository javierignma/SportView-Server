from sqlmodel import SQLModel, Field
from typing import Optional

class AttendanceRequestSchema(SQLModel, table=False):
    instructor_id: int = Field(foreign_key="user.id")
    student_id: int = Field(foreign_key="student.id")
    present: Optional[bool]