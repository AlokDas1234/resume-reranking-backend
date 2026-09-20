import os
import shutil
from app.services.vector_store import add_resume_to_vector_store

from fastapi import (
    APIRouter,
    File,
    UploadFile,
    HTTPException,
    Depends,
)

from sqlalchemy.orm import Session

from app.database.database import get_db
from app.auth.security import get_current_user
from app.models.user import User
from app.models.resume import Resume
from app.schemas.resume import ResumeResponse

from app.services.text_extractor import (
    extract_pdf_text,
    extract_docx_text,
)


router = APIRouter(
    prefix="/resume",
    tags=["Resume"]
)


UPLOAD_DIR = "app/uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post(
    "/upload",
    response_model=ResumeResponse
)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    # 1. Get file extension
    extension = os.path.splitext(file.filename)[1].lower()

    # 2. Allow only PDF and DOCX
    if extension not in [".pdf", ".docx"]:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are allowed."
        )

    # 3. Save file
    file_path = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    # 4. Extract text
    if extension == ".pdf":
        extracted_text = extract_pdf_text(file_path)
    else:
        extracted_text = extract_docx_text(file_path)

    # 5. Create Resume database object
    resume = Resume(
        filename=file.filename,
        filepath=file_path,
        content=extracted_text,
        user_id=current_user.id
    )

    # 6. Save to PostgreSQL
    db.add(resume)
    db.commit()
    db.refresh(resume)

    # 7. Add resume to Chroma
    add_resume_to_vector_store(
        resume_id=resume.id,
        filename=resume.filename,
        content=resume.content,
        user_id=current_user.id
    )

    # 8. Return saved resume
    return resume

@router.get("/")
def get_my_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    resumes = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .all()
    )

    return resumes


# --------------------------------------------------
# GET SINGLE RESUME
# --------------------------------------------------

@router.get("/{resume_id}")
def get_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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

    return {
        "id": resume.id,
        "filename": resume.filename,
        "filepath": resume.filepath,
        "content": resume.content,
        "user_id": resume.user_id
    }

# --------------------------------------------------
# DELETE RESUME
# --------------------------------------------------

@router.delete("/{resume_id}")
def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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

    # Delete physical file
    if os.path.exists(resume.filepath):
        os.remove(resume.filepath)

    # Delete database record
    db.delete(resume)
    db.commit()

    return {
        "message": "Resume deleted successfully",
        "resume_id": resume_id
    }