from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from ..core.database import get_session
from ..models.user import User
from ..schemas.user import UserResponseSchema
import urllib.parse

router = APIRouter()

@router.post("/", response_model=UserResponseSchema)
def create_user(user: User, session: Session = Depends(get_session)):
    
    statement = select(User).where(User.email == user.email)
    result = session.exec(statement)

    if result.first():
        raise HTTPException(status_code=409, detail="Email is already in use.")

    try:
        session.add(user)
        session.commit()
        session.refresh(user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error has ocurred: {e}")
    return user

@router.get("/id/{user_id}", response_model=UserResponseSchema)
def read_user_by_id(user_id: int, session: Session = Depends(get_session)):
    try:  
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error has ocurred: {e}")

@router.get("/email/{user_email}", response_model=UserResponseSchema)
def read_user_by_email(user_email: str, session: Session = Depends(get_session)):
    try:
        user_email = urllib.parse.unquote(user_email)
        statement = select(User).where(User.email == user_email)
        result = session.exec(statement)
        user = result.first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        else:
            return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error has ocurred: {e}")
