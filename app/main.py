from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.database import create_db_and_tables
from .models.attendance import Attendance
from .models.student import Student, StudentProgress
from .models.user import User

app = FastAPI(
    title="SportView API",
    description="API for managing students, instructors, attendance, and more",
    version="1.0.0"
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    print("[main - on_startup] Trying to create database and tables")
    create_db_and_tables()

@app.get("/")
async def root():
    return {"message": "Welcome to SportView API!"}