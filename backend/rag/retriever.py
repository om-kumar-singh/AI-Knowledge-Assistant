"""Query embedding and similarity search over ChromaDB (retrieval only, no LLM)."""

from core.config import get_settings
from rag.ingest import get_vector_store


def retrieve(query: str, k: int | None = None) -> list[str]:
    """
    Embed the query with the same local model used at ingest time and return
    the top-k most similar chunk texts.
    """
    if k is None:
        k = get_settings().rag_default_top_k
    k = max(1, min(k, 50))
    store = get_vector_store()
    docs = store.similarity_search(query, k=k)
    return [d.page_content for d in docs]
