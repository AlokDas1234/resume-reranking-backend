from fastapi import FastAPI
from app.database.database import Base, engine
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.api.users import router as user_router
from app.api.resume import router as resume_router
from app.models.user import User
from app.models.resume import Resume
from app.models.job import JobDescription
from app.api.jobs import router as job_router
from app.models.ranking import ResumeRanking
from fastapi.middleware.cors import CORSMiddleware
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Resume Ranker API",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(user_router)
app.include_router(resume_router)
app.include_router(job_router)
@app.get("/")
def root():
    return {"message": "Resume Ranker API is running."}


@app.get("/health/db")
def check_database(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"message": "Database connected successfully"}

