from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

from app.core.settings import settings


class ResumeRanking(BaseModel):
    score: int = Field(
        description="Overall resume match score from 0 to 100"
    )

    skills_match: list[str] = Field(
        description="Skills from the resume that match the job"
    )

    experience_match: str = Field(
        description="Explanation of how the candidate's experience matches"
    )

    technology_match: list[str] = Field(
        description="Technologies from the resume that match the job"
    )

    reason: str = Field(
        description="Short explanation of the overall match"
    )


llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=settings.OPENAI_API_KEY,
    temperature=0
)

structured_llm = llm.with_structured_output(
    ResumeRanking
)


def rerank_resume(
    job_description: str,
    resume_content: str
):

    prompt = f"""
You are an expert technical recruiter.

Compare the following job description with the candidate's resume.

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_content}

Evaluate the candidate based on:

1. Skills match
2. Years of experience
3. Technology match
4. Responsibilities match
5. Overall relevance

Give an overall score from 0 to 100.

Do not give a high score simply because the candidate has some matching
keywords. Consider the actual relevance of the candidate's experience.
"""

    result = structured_llm.invoke(prompt)

    return result.model_dump()