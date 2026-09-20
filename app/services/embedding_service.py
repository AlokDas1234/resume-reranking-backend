from langchain_openai import OpenAIEmbeddings
from app.core.settings import settings

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=settings.OPENAI_API_KEY
)


def create_embedding(text: str):
    return embeddings.embed_query(text)