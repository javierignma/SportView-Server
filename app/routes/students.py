from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session
from ..core.database import get_session
from ..models.student import Student

router = APIRouter()

@router.post(
    "/students/",
    response_model=Student
)
def create_student(student: Student, session: Session = Depends(get_session)):
    try:
        session.add(student)
        session.commit()
        session.refresh(student)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error has ocurred: {e}")
    return student
'''
@router.get()
def read_student():
    pass

@router.put()
def update_student():
    pass

@router.delete()
def delete_student():
    pass
'''
