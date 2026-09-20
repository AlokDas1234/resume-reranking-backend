from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from app.core.settings import settings


embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=settings.OPENAI_API_KEY
)


vector_store = Chroma(
    collection_name="resume_collection",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)

def add_resume_to_vector_store(
    resume_id: int,
    filename: str,
    content: str,
    user_id: int
):
    vector_store.add_texts(
        texts=[content],
        metadatas=[
            {
                "resume_id": resume_id,
                "filename": filename,
                "user_id": user_id
            }
        ],
        ids=[f"resume_{resume_id}"]
    )

def search_resumes_for_job(
    job_description: str,
    user_id: int,
    k: int = 5
):
    results = vector_store.similarity_search_with_score(
        job_description,
        k=k,
        filter={"user_id": user_id}
    )

    ranked_results = []

    for document, distance in results:
        # Convert distance into a simple score
        score = 1 / (1 + distance)

        ranked_results.append({
            "resume_id": document.metadata["resume_id"],
            "filename": document.metadata["filename"],
            "score": round(score * 100, 2)
        })

    # Highest score first
    ranked_results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return ranked_results