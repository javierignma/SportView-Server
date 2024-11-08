from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session, select, update
import urllib

from app.models.attendance import Attendance
from app.services.jwt_service import token_verifier
from ..core.database import get_session
from ..models.student import Student, StudentProgress

router = APIRouter()

@router.post(
    "/",
    response_model=Student
)
def create_student(student: Student, session: Session = Depends(get_session), dependencies = [Depends(token_verifier)]):
    try:
        session.add(student)
        session.commit()
        session.refresh(student)
    except Exception as e:
        print(f"An error has ocurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    return student

@router.get("/id/{student_id}", response_model=Student)
def read_student_by_id(student_id: int, session: Session = Depends(get_session), dependencies = [Depends(token_verifier)]):
    try:  
        student = session.get(Student, student_id)
    except Exception as e:
        print(f"An error has ocurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
        
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return student

@router.get("/{instructor_id}", response_model=list[Student])
def read_students(instructor_id: int, session: Session = Depends(get_session), dependencies = [Depends(token_verifier)]):
    try:
        statement = select(Student).where(Student.instructor_id == instructor_id)
        result = session.exec(statement)
        students = result.all()
    except Exception as e:
        print(f"An error has ocurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    if not students:
        raise HTTPException(status_code=404, detail="Students not found")
    
    return students

@router.get("/email/{student_email}", response_model=Student)
def read_student_by_email(student_email: str, session: Session = Depends(get_session), dependencies = [Depends(token_verifier)]):
    try:
        student_email = urllib.parse.unquote(student_email)

        statement = select(Student).where(Student.email == student_email)
        result = session.exec(statement)
        student = result.first()
    except Exception as e:
        print(f"An error has ocurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return student

@router.get("/rut/{student_rut}", response_model=Student)
def read_student_by_rut(student_rut: str, session: Session = Depends(get_session), dependencies = [Depends(token_verifier)]):
    try:
        student_rut = urllib.parse.unquote(student_rut)

        statement = select(Student).where(Student.rut == student_rut)
        result = session.exec(statement)
        student = result.first()
    except Exception as e:
        print(f"An error has ocurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return student

@router.put("/edit/id/{student_id}", response_model=Student)
def update_student(student_id: int, student_update: Student, session: Session = Depends(get_session), dependencies = [Depends(token_verifier)]):
    try:
        student = session.get(Student, student_id)
    except Exception as e:
        print(f"An error has ocurred searching for the student: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    update_data = student_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(student, key, value)

    try:
        session.add(student)
        session.commit()
        session.refresh(student)
    except Exception as e:
        print(f"An error has ocurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
        
    return student

@router.post("/progress/id/", response_model=StudentProgress)
def post_student_progress(student_progress: StudentProgress, session: Session = Depends(get_session), dependencies = [Depends(token_verifier)]):
    try:
        session.add(student_progress)
        session.commit()
        session.refresh(student_progress)
    except Exception as e:
        print(f"An error has ocurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    return student_progress

@router.delete("/delete/id/{student_id}")
def delete_student(student_id: int, session: Session = Depends(get_session), dependencies = [Depends(token_verifier)]):

    try:
        statement = select(Attendance).where(Attendance.student_id == student_id)
        result = session.exec(statement)
        attendance = result.first()

        if attendance:
            session.delete(attendance)
            session.commit()

    except Exception as e:
        print(f"An error has ocurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
    # Do the same with StudentProgress

    try:
        statement = select(Student).where(Student.id == student_id)
        result = session.exec(statement)
        student = result.first()

        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        session.delete(student)
        session.commit()

        return {"message": "Student deleted successfully"}
    except Exception as e:
        print(f"An error has ocurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")