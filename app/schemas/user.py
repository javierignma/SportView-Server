from sqlmodel import SQLModel, Field
from typing import Optional

class UserResponseSchema(SQLModel, table=False):
    email: str
    first_name: Optional[str]
    last_name: Optional[str]

class UserCredentialsSchema(SQLModel, table=False):
    email: str
    password: str