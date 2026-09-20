from pydantic import BaseModel
from datetime import datetime


class ResumeResponse(BaseModel):
    id: int
    filename: str
    filepath: str
    content: str
    uploaded_at: datetime
    user_id: int

    class Config:
        from_attributes = True