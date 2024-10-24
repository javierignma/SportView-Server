from sqlmodel import SQLModel, create_engine, Session
from .config import DATABASE_URL

print(f"[core.database] DATABASE_URL: {DATABASE_URL}")

engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session