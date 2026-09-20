from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.models.job import JobDescription


def get_resumes_for_job(
    db: Session,
    job: JobDescription
):
    resumes = (
        db.query(Resume)
        .filter(Resume.user_id == job.user_id)
        .all()
    )

    return resumes