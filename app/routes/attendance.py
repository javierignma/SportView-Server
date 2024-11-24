from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import Float, Integer, cast, func
from sqlmodel import Session, and_, select, update
from datetime import date as Date

from app.models.attendance import Attendance
from app.models.student import Student
from app.schemas.attendance import AttendanceAvg, AttendanceResponse
from app.services.jwt_service import token_verifier
from ..core.database import get_session

router = APIRouter()

@router.post(
    "/"
)
def add_attendances(attendances: list[Attendance], session: Session = Depends(get_session), dependencies = [Depends(token_verifier)]):   
    try:
        session.add_all(attendances)
        session.commit()
        
        for attendance in attendances:
            session.refresh(attendance)

    except Exception as e:
        print(f"An error has ocurred on third section: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    

    return {"message": "Attendance added."}

@router.get(
    "/all/{instructor_id}/{date}",
    response_model=list[AttendanceResponse]
)
def get_attendances(instructor_id: int, date: Date, session: Session = Depends(get_session), dependencies = [Depends(token_verifier)]):
    try:
        statement = (
            select(
                Attendance.id,
                Attendance.instructor_id,
                Attendance.student_id,
                (Student.name).label("student_name"),
                Attendance.date,
                Attendance.present
            )
            .join(Student, Attendance.student_id == Student.id)
            .where(
                and_(
                    Attendance.instructor_id == instructor_id,
                    Attendance.date == date
                )
            )
        )
        result = session.exec(statement)
        attendances = result.all()
    except Exception as e:
        print(f"An error has ocurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    if not attendances:
        raise HTTPException(status_code=404, detail="Attendances not found")
    
    return attendances

@router.put("/")
def update_attendances(
    attendances: list[Attendance],
    session: Session = Depends(get_session),
    dependencies = [Depends(token_verifier)]
):
    try:
        with session.begin():
            for attendance in attendances:
                existing_attendance = session.get(Attendance, attendance.id)

                if existing_attendance:
                    existing_attendance.instructor_id = attendance.instructor_id
                    existing_attendance.student_id = attendance.student_id
                    existing_attendance.date = attendance.date
                    existing_attendance.present = attendance.present
                else:
                    raise HTTPException(status_code=404, detail=f"Attendance with id {attendance.id} not found")

        return {"message": "Attendances updated successfully"}

    except HTTPException as e:
        print(f"An error has ocurred: {e}")
        session.rollback()

    except Exception as e:
        session.rollback()
        print(f"An error has ocurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{attendance_id}")
def delete_attendance(attendance_id: int, session: Session = Depends(get_session), dependencies = [Depends(token_verifier)]):
    try:
        statement = select(Attendance).where(Attendance.id == attendance_id)
        result = session.exec(statement)
        attendance = result.first()

        if not attendance:
            raise HTTPException(status_code=404, detail="Attendance not found")
        
        session.delete(attendance)
        session.commit()

        return {"message": "Attendance deleted successfully"}
    except Exception as e:
        print(f"An error has ocurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get(
    "/dates/{instructor_id}",
    response_model=list[Date]
)
def get_dates(instructor_id: int, session: Session = Depends(get_session)):
    try:
        statement = select(Attendance.date).where(Attendance.instructor_id == instructor_id).distinct().order_by(Attendance.date)
        results = session.exec(statement).all()
    except Exception as e:
        print(f"An error has ocurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    if not results:
        raise HTTPException(status_code=404, detail="Dates not found")
    
    return results

@router.get("/avg/{student_id}", response_model=AttendanceAvg)
def get_avg_attendance(
    student_id: int,
    session: Session = Depends(get_session),
):
    try:
        query = (
            select(func.avg(cast(Attendance.present, Integer)).label("avg_attendance"))
            .where(Attendance.student_id == student_id)
        )
        result = session.exec(query).first()
    except Exception as e:
        print(f"An error has ocurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    if result is None:
        raise HTTPException(status_code=404, detail="Student not found or no attendance data.")
    return AttendanceAvg(student_id=student_id, avg_attendance=result)

    