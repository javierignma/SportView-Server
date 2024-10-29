from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from ..core.database import get_session
from ..models.user import User
from ..schemas.user import UserResponseSchema, UserCredentialsSchema
from ..services.password_service import hash_password, verify_password 
from ..services.jwt_service import create_access_token, create_refresh_token, token_verifier
import urllib.parse

router = APIRouter()

@router.post("/", response_model=UserResponseSchema)
def create_user(user: User, session: Session = Depends(get_session)):
    try:
        statement = select(User).where(User.email == user.email)
        result = session.exec(statement)
    except Exception as e:
        print(f"An error has ocurred: {e}")

    if result.first():
        raise HTTPException(status_code=409, detail="Email is already in use.")

    try:
        user.password = hash_password(user.password)
        session.add(user)
        session.commit()
        session.refresh(user)
    except Exception as e:
        print(f"An error has ocurred: {e}")
    return user

@router.get("/id/{user_id}", response_model=UserResponseSchema)
def read_user_by_id(user_id: int, session: Session = Depends(get_session), dependencies = [Depends(token_verifier)]):
    try:  
        user = session.get(User, user_id)
    except Exception as e:
        print(f"An error has ocurred: {e}")
        
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@router.get("/email/{user_email}", response_model=UserResponseSchema)
def read_user_by_email(user_email: str, session: Session = Depends(get_session), dependencies = [Depends(token_verifier)]):
    try:
        user_email = urllib.parse.unquote(user_email)

        statement = select(User).where(User.email == user_email)
        result = session.exec(statement)
        user = result.first()
    except Exception as e:
        print(f"An error has ocurred: {e}")

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@router.post("/login/", response_model=UserResponseSchema)
def login(user_credentials: UserCredentialsSchema, session: Session = Depends(get_session)):
    try:
        statement = select(User).where(User.email == user_credentials.email)
        result = session.exec(statement)
        user = result.first()
    except Exception as e:
        print(f"An error has ocurred: {e}")

    if not user or not verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=401, detail="Wrong credetials.")

    # Generate token
    access_token = create_access_token({"sub": user.email})
    #refresh_token = create_refresh_token({"sub": user.email})
    
    user = UserResponseSchema(
        email=user.email, 
        first_name=user.first_name, 
        last_name=user.last_name, 
        access_token=access_token, 
        #refresh_token=refresh_token
    )
    
    return user

@router.get("/verify-token/")
def verify_token(dependencies = Depends(token_verifier)):
    return {"message": "Valid token."}