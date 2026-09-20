from pydantic import BaseModel
from datetime import datetime


class JobCreate(BaseModel):
    title: str
    description: str


class JobResponse(BaseModel):
    id: int
    title: str
    description: str
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True