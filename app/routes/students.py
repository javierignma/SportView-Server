from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlmodel import Session, and_, select, update
import urllib

from app.models.attendance import Attendance
from app.schemas.students import StudentProgressAverage
from app.services.jwt_service import token_verifier
from ..core.database import get_session
from ..models.student import Student, StudentProgress
from datetime import date as Date

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
    
@router.post(
    "/progress/"
)
def create_student_progress(student_progress: StudentProgress, session: Session = Depends(get_session), dependencies = [Depends(token_verifier)]):
    try:
        session.add(student_progress)
        session.commit()
        session.refresh(student_progress)
    except Exception as e:
        print(f"An error has ocurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    return {"message": "Student progress created successfully"}

@router.get("/progress/student/{student_id}/{date}", response_model=StudentProgress)
def read_student_progress(student_id: int, date: Date, session: Session = Depends(get_session), dependencies = [Depends(token_verifier)]):
    try: 
        statement = select(StudentProgress).where(
            and_(StudentProgress.student_id == student_id, StudentProgress.progress_date == date)
        )
        result = session.exec(statement).first()
    except Exception as e:
        print(f"An error has ocurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
        
    if not result:
        raise HTTPException(status_code=404, detail="Student progress not found")
    
    student_progress = result

    return student_progress

@router.get("/progress/student-avg/{student_id}", response_model=StudentProgressAverage)
def read_student_progress_average(student_id: int, session: Session = Depends(get_session), dependencies = [Depends(token_verifier)]):
    try: 
        pre_statement = select(StudentProgress).where(StudentProgress.student_id == student_id)

        pre_result = session.exec(pre_statement).first()

        if not pre_result:
            result = StudentProgressAverage(
                technique_avg=0,
                physique_avg=0,
                combat_iq_avg=0,
            )

            return result

        statement = (
            select(
                func.avg(StudentProgress.technique).label("technique_avg"),
                func.avg(StudentProgress.physique).label("physique_avg"),
                func.avg(StudentProgress.combat_iq).label("combat_iq_avg")
            )
            .where(StudentProgress.student_id == student_id)
        )
        result = session.exec(statement).first()
    except Exception as e:
        print(f"An error has ocurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
        
    if not result:
        raise HTTPException(status_code=404, detail="Student progress average not found")
    
    student_progress = result

    return student_progress

@router.put("/progress/{student_progress_id}", response_model=StudentProgress)
def update_student_progress(student_progress_id: int, student_progress_update: StudentProgress, session: Session = Depends(get_session), dependencies = [Depends(token_verifier)]):
    try:
        student_progress = session.get(StudentProgress, student_progress_id)
    except Exception as e:
        print(f"An error has ocurred searching for the student progress: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
    if not student_progress:
        raise HTTPException(status_code=404, detail="Student progress not found")

    update_data = student_progress_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(student_progress, key, value)

    try:
        session.add(student_progress)
        session.commit()
        session.refresh(student_progress)
    except Exception as e:
        print(f"An error has ocurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
        
    return student_progress

@router.get("/progress/dates/{instructor_id}/{student_id}", response_model=list[Date])
def get_progress_dates(instructor_id: int, student_id: int, session: Session = Depends(get_session), dependencies = [Depends(token_verifier)]):
    try: 
        statement = select(StudentProgress.progress_date).join(
            Student, Student.id == StudentProgress.student_id
        ).where(and_(Student.instructor_id == instructor_id, Student.id == student_id)).distinct().order_by(StudentProgress.progress_date)
        results = session.exec(statement).all()
    except Exception as e:
        print(f"An error has ocurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
        
    if not results:
        raise HTTPException(status_code=404, detail="Student progress dates not found")
    
    dates = results

    return dates