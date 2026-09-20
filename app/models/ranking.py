from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import UniqueConstraint
from app.database.database import Base


class ResumeRanking(Base):
    __tablename__ = "resume_rankings"
    __table_args__ = (
        UniqueConstraint(
            "job_id",
            "resume_id",
            name="unique_job_resume"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    job_id = Column(Integer,ForeignKey("job_descriptions.id"),nullable=False)

    resume_id = Column(Integer,ForeignKey("resumes.id"),nullable=False)

    score = Column(Integer, nullable=False)

    rank = Column(Integer, nullable=False)

    skills_match = Column(Text, nullable=True)

    experience_match = Column(Text, nullable=True)

    technology_match = Column(Text, nullable=True)

    reason = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True),server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    job = relationship(
        "JobDescription",
        back_populates="rankings"
    )

    resume = relationship(
        "Resume",
        back_populates="rankings"
    )