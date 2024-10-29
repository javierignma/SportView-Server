from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import HTTPException, Header, Cookie
from ..core.config import SECRET_KEY, ALGORITHM, REFRESH_SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS

pwd_context = CryptContext(schemes=["bcrypt"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + (timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + (timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)

async def token_verifier(
    authorization: str = Header(...),
    #refresh_token: str = Cookie(None)
):
    if authorization:
        try:
            access_token = authorization.split(" ")[1]
            print("access token: ", access_token)
            jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
            return
        except JWTError:
            '''
            if refresh_token:
                try:
                    payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
                    user_email = payload.get("sub")
                    new_access_token = create_access_token({"sub": user_email})
                    return {"user_email": user_email, "new_access_token": new_access_token}
                except JWTError:
                    raise HTTPException(status_code=403, detail="Invalid refresh token")
            else:
            '''
            raise HTTPException(status_code=401, detail="Access token expired, refresh token required")
            
    raise HTTPException(status_code=401, detail="Authorization token required")