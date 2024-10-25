from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import students, users
from .core.database import create_db_and_tables

app = FastAPI(
    title="SportView API",
    description="API for managing students, instructors, attendance, and more",
    version="1.0.0",
)

app.include_router(students.router, prefix="/api/v1", tags=["Students"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])

origins = ["http://localhost:8100"]

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