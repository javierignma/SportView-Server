from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session, and_, select, update
from datetime import date as Date

from app.models.attendance import Attendance, Dates
from app.schemas.attendance import AttendanceRequestSchema
from app.services.jwt_service import token_verifier
from ..core.database import get_session

router = APIRouter()

@router.post(
    "/{year}/{month}/{day}"
)
def add_attendance(year: int, month: int, day: int, attendances: list[AttendanceRequestSchema], session: Session = Depends(get_session), dependencies = [Depends(token_verifier)]):
    dates_id = None
    
    date = Date(year, month, day)

    try:
        statement = select(Dates).where(Dates.date == date)
        result = session.exec(statement)
        dates_id = result.first()
    except Exception as e:
        print(f"An error has ocurred on first section: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
    if not dates_id:
        try:
            date_object = Dates(date=date)
            session.add(date_object)
            session.commit()
            session.refresh(date_object)

            statement = select(Dates).where(Dates.date == date)
            result = session.exec(statement)
            dates_id = result.first()
        except Exception as e:
            print(f"An error has ocurred on second section: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    try:
        new_attendances = []
        for attendance in attendances:
            new_attendance = Attendance(
                id=None,
                instructor_id=attendance.instructor_id,
                student_id=attendance.student_id,
                dates_id=dates_id.id,
                present=attendance.present,
            )
            print(new_attendance)
            new_attendances.append(new_attendance)

        session.add_all(new_attendances)
        session.commit()
        
        for new_attendance in new_attendances:
            session.refresh(new_attendance)

    except Exception as e:
        print(f"An error has ocurred on third section: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    

    return {"message": "Attendance added."}

@router.get(
    "/{instructor_id}/{year}/{month}/{day}",
    response_model=list[Attendance]
)
def get_attendances(instructor_id: int, year: int, month: int, day: int, session: Session = Depends(get_session), dependencies = [Depends(token_verifier)]):
    dates_id = None
    
    date = Date(year, month, day)

    try:
        statement = select(Dates).where(Dates.date == date)
        result = session.exec(statement)
        dates_id = result.first()
    except Exception as e:
        print(f"An error has ocurred on first section: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
    if not dates_id:
        raise HTTPException(status_code=404, detail="Date not found")
    
    dates_id = dates_id.id
    
    try:
        statement = select(Attendance).where(and_(
            Attendance.instructor_id == instructor_id,
            Attendance.dates_id == dates_id
        ))
        result = session.exec(statement)
        attendances = result.all()
    except Exception as e:
        print(f"An error has ocurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    if not attendances:
        raise HTTPException(status_code=404, detail="Attendances not found")
    
    return attendances

@router.put("/{attendance_id}")
def update_attendance(attendance_id: int, attendance_update: Attendance, session: Session = Depends(get_session), dependencies = [Depends(token_verifier)]):
    try:
        attendance = session.get(Attendance, attendance_id)
    except Exception as e:
        print(f"An error has ocurred searching for the attendance: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")

    update_data = attendance_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(attendance, key, value)

    try:
        session.add(attendance)
        session.commit()
        session.refresh(attendance)
    except Exception as e:
        print(f"An error has ocurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
        
    return {"message": "Attendance updated."}

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