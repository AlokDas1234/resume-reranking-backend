# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
#
# from app.database.database import get_db
# from app.models.job import JobDescription
# from app.schemas.job import JobCreate, JobResponse
# from app.auth.security import get_current_user
# from app.services.resume_matcher import get_resumes_for_job
# from fastapi import APIRouter, Depends, HTTPException
# from app.models.user import User
#
# #Temporary 2
# from app.services.embedding_service import create_embedding
#
# #Test3
# from app.models.resume import Resume
# from app.services.vector_store import add_resume_to_vector_store
#
#
#
#
#
# router = APIRouter(
#     prefix="/jobs",
#     tags=["Jobs"]
# )
#
#
#
#
# #Test3
# @router.post("/{job_id}/test-vector")
# def test_vector_store(
#     job_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     # Get the job belonging to the logged-in user
#     job = (
#         db.query(JobDescription)
#         .filter(
#             JobDescription.id == job_id,
#             JobDescription.user_id == current_user.id
#         )
#         .first()
#     )
#
#     if job is None:
#         raise HTTPException(
#             status_code=404,
#             detail="Job description not found"
#         )
#
#     # Get one resume belonging to the logged-in user
#     resume = (
#         db.query(Resume)
#         .filter(
#             Resume.user_id == current_user.id
#         )
#         .first()
#     )
#
#     if resume is None:
#         raise HTTPException(
#             status_code=404,
#             detail="No resume found"
#         )
#
#     # Add resume to Chroma
#     add_resume_to_vector_store(
#         resume_id=resume.id,
#         filename=resume.filename,
#         content=resume.content
#     )
#
#     return {
#         "message": "Resume added to vector store",
#         "resume_id": resume.id,
#         "filename": resume.filename
#     }
#
# @router.post("/", response_model=JobResponse)
# def create_job(
#     job: JobCreate,
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user)
# ):
#
#     new_job = JobDescription(
#         title=job.title,
#         description=job.description,
#         user_id=current_user.id
#     )
#
#     db.add(new_job)
#     db.commit()
#     db.refresh(new_job)
#
#     return new_job
#
#
#
# #Temporary 2
# from app.services.embedding_service import create_embedding
# @router.get("/test-embedding")
# def test_embedding():
#     vector = create_embedding(
#         "React developer with 5 years of experience"
#     )
#
#     return {
#         "dimensions": len(vector),
#         "first_values": vector[:5]
#     }
#
#
# @router.get("/{job_id}", response_model=JobResponse)
# def get_job(
#     job_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     job = (
#         db.query(JobDescription)
#         .filter(
#             JobDescription.id == job_id,
#             JobDescription.user_id == current_user.id
#         )
#         .first()
#     )
#
#     if job is None:
#         raise HTTPException(
#             status_code=404,
#             detail="Job description not found"
#         )
#
#     return job
#
#
#
# #Temporary
# @router.get("/{job_id}/resumes")
# def get_job_resumes(
#     job_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     job = (
#         db.query(JobDescription)
#         .filter(
#             JobDescription.id == job_id,
#             JobDescription.user_id == current_user.id
#         )
#         .first()
#     )
#
#     if job is None:
#         raise HTTPException(
#             status_code=404,
#             detail="Job description not found"
#         )
#
#     resumes = get_resumes_for_job(db, job)
#
#     return [
#         {
#             "id": resume.id,
#             "filename": resume.filename,
#             "user_id": resume.user_id
#         }
#         for resume in resumes
#     ]
#

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.job import JobDescription
from app.models.resume import Resume
from app.models.user import User

from app.schemas.job import JobCreate, JobResponse

from app.auth.security import get_current_user

from app.services.resume_matcher import get_resumes_for_job
from app.services.embedding_service import create_embedding
from app.services.vector_store import add_resume_to_vector_store
from app.services.vector_store import search_resumes_for_job
from app.services.reranker import rerank_resume
from app.models.ranking import ResumeRanking


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)


# --------------------------------------------------
# 1. CREATE JOB
# --------------------------------------------------

#To see the jobs in frontend
@router.post("/", response_model=JobResponse)
def create_job(
    job: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_job = JobDescription(
        title=job.title,
        description=job.description,
        user_id=current_user.id
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return new_job


@router.get("/")
def get_my_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    jobs = (
        db.query(JobDescription)
        .filter(JobDescription.user_id == current_user.id)
        .order_by(JobDescription.created_at.desc())
        .all()
    )

    return jobs


# --------------------------------------------------
# 2. TEST EMBEDDING
# --------------------------------------------------

@router.get("/test-embedding")
def test_embedding():

    vector = create_embedding(
        "React developer with 5 years of experience"
    )

    return {
        "dimensions": len(vector),
        "first_values": vector[:5]
    }


# --------------------------------------------------
# 3. TEST VECTOR STORE
# --------------------------------------------------

@router.post("/{job_id}/test-vector")
def test_vector_store(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    job = (
        db.query(JobDescription)
        .filter(
            JobDescription.id == job_id,
            JobDescription.user_id == current_user.id
        )
        .first()
    )

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job description not found"
        )

    resume = (
        db.query(Resume)
        .filter(
            Resume.user_id == current_user.id
        )
        .first()
    )

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="No resume found"
        )

    add_resume_to_vector_store(
        resume_id=resume.id,
        filename=resume.filename,
        content=resume.content
    )

    return {
        "message": "Resume added to vector store",
        "resume_id": resume.id,
        "filename": resume.filename
    }


# --------------------------------------------------
# 4. GET JOB RESUMES
# --------------------------------------------------

@router.get("/{job_id}/resumes")
def get_job_resumes(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    job = (
        db.query(JobDescription)
        .filter(
            JobDescription.id == job_id,
            JobDescription.user_id == current_user.id
        )
        .first()
    )

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job description not found"
        )

    resumes = get_resumes_for_job(db, job)

    return [
        {
            "id": resume.id,
            "filename": resume.filename,
            "user_id": resume.user_id
        }
        for resume in resumes
    ]


# --------------------------------------------------
# 5. GET SINGLE JOB
# --------------------------------------------------

@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    job = (
        db.query(JobDescription)
        .filter(
            JobDescription.id == job_id,
            JobDescription.user_id == current_user.id
        )
        .first()
    )

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job description not found"
        )

    return job


# --------------------------------------------------
# 6. UPDATE JOB
# --------------------------------------------------

@router.patch("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_data: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    job = (
        db.query(JobDescription)
        .filter(
            JobDescription.id == job_id,
            JobDescription.user_id == current_user.id
        )
        .first()
    )

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job description not found"
        )

    job.title = job_data.title
    job.description = job_data.description

    db.commit()
    db.refresh(job)

    return job

# --------------------------------------------------
# 7. DELETE JOB
# --------------------------------------------------

@router.delete("/{job_id}", response_model=JobResponse)
def delete_job(
    job_id: int,

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    job = (
        db.query(JobDescription)
        .filter(
            JobDescription.id == job_id,
            JobDescription.user_id == current_user.id
        )
        .first()
    )

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job description not found"
        )
    db.delete(job)
    db.commit()
    return job

@router.get("/{job_id}/test-search")
def test_search(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job = (
        db.query(JobDescription)
        .filter(
            JobDescription.id == job_id,
            JobDescription.user_id == current_user.id
        )
        .first()
    )

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job description not found"
        )

    results = search_resumes_for_job(
        job_description=job.description,
        user_id=current_user.id,
        k=5
    )

    return results


@router.get("/{job_id}/test-reranker/{resume_id}")
def test_reranker(
        job_id: int,
        resume_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # Get the job belonging to the logged-in user
    job = (
        db.query(JobDescription)
        .filter(
            JobDescription.id == job_id,
            JobDescription.user_id == current_user.id
        )
        .first()
    )

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job description not found"
        )

    # Get the resume belonging to the logged-in user
    resume = (
        db.query(Resume)
        .filter(
            Resume.id == resume_id,
            Resume.user_id == current_user.id
        )
        .first()
    )

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

    # Send job + resume to the LLM
    result = rerank_resume(
        job_description=job.description,
        resume_content=resume.content
    )

    return {
        "resume_id": resume.id,
        "filename": resume.filename,
        "result": result
    }

@router.get("/{job_id}/rank-resumes")
def rank_resumes(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Get the job belonging to the logged-in user
    job = (
        db.query(JobDescription)
        .filter(
            JobDescription.id == job_id,
            JobDescription.user_id == current_user.id
        )
        .first()
    )

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job description not found"
        )

    # 2. Get top resumes from Chroma
    results = search_resumes_for_job(
        job_description=job.description,
        user_id=current_user.id,
        k=5
    )

    ranked_resumes = []

    # 3. Rerank each resume using the LLM
    for result in results:

        resume_id = result["resume_id"]

        resume = (
            db.query(Resume)
            .filter(
                Resume.id == resume_id,
                Resume.user_id == current_user.id
            )
            .first()
        )

        if resume is None:
            continue

        rerank_result = rerank_resume(
            job_description=job.description,
            resume_content=resume.content
        )

        ranked_resumes.append({
            "resume_id": resume.id,
            "filename": resume.filename,
            "score": rerank_result["score"],
            "skills_match": rerank_result["skills_match"],
            "experience_match": rerank_result["experience_match"],
            "technology_match": rerank_result["technology_match"],
            "reason": rerank_result["reason"]
        })

    # 4. Sort by score
    ranked_resumes.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    # 5. Assign rank
    for index, resume in enumerate(ranked_resumes, start=1):
        resume["rank"] = index

    # 6. Save ranking results to PostgreSQL
    #    Update existing ranking or create a new one

    for resume in ranked_resumes:

        ranking = (
            db.query(ResumeRanking)
            .filter(
                ResumeRanking.job_id == job.id,
                ResumeRanking.resume_id == resume["resume_id"]
            )
            .first()
        )

        if ranking:

            # Existing ranking → UPDATE

            ranking.score = resume["score"]

            ranking.rank = resume["rank"]

            ranking.skills_match = ", ".join(
                resume["skills_match"]
            )

            ranking.experience_match = (
                resume["experience_match"]
            )

            ranking.technology_match = ", ".join(
                resume["technology_match"]
            )

            ranking.reason = resume["reason"]

        else:

            # No existing ranking → CREATE

            ranking = ResumeRanking(
                job_id=job.id,
                resume_id=resume["resume_id"],
                score=resume["score"],
                rank=resume["rank"],
                skills_match=", ".join(
                    resume["skills_match"]
                ),
                experience_match=resume["experience_match"],
                technology_match=", ".join(
                    resume["technology_match"]
                ),
                reason=resume["reason"]
            )

            db.add(ranking)

    db.commit()

    return ranked_resumes