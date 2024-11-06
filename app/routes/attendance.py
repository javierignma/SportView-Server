from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session, and_, select, update
from datetime import date as Date

from app.models.attendance import Attendance
from app.services.jwt_service import token_verifier
from ..core.database import get_session

router = APIRouter()

@router.post(
    "/"
)
def add_attendance(attendance: Attendance, session: Session = Depends(get_session), dependencies = [Depends(token_verifier)]):
    try:
        session.add(attendance)
        session.commit()
        session.refresh(attendance)
    except Exception as e:
        print(f"An error has ocurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    return {"message": "Attendance added."}

@router.get(
    "/{instructor_id}/{date}",
    response_model=list[Attendance]
)
def get_attendances(instructor_id: int, date: Date, session: Session = Depends(get_session), dependencies = [Depends(token_verifier)]):
    try:
        statement = select(Attendance).where(and_(
            Attendance.instructor_id == instructor_id,
            Attendance.date == date
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