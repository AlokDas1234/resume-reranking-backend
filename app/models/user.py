from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String, unique=True, nullable=False)

    email = Column(String, unique=True, nullable=False)

    hashed_password = Column(String, nullable=False)

    resumes = relationship(
        "Resume",
        back_populates="user",
        cascade="all, delete"
    )

    job_descriptions = relationship(
        "JobDescription",
        back_populates="user",
        cascade="all, delete"
    )