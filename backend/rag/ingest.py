"""Load documents, chunk, embed with sentence-transformers, and persist in ChromaDB."""

from __future__ import annotations

import logging
import threading
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

from core.config import get_settings

logger = logging.getLogger(__name__)

CHROMA_COLLECTION_NAME = "knowledge_base"

_embeddings_lock = threading.Lock()
_embeddings: HuggingFaceEmbeddings | None = None


def _backend_root() -> Path:
    return Path(__file__).resolve().parent.parent


def get_embedding_model() -> HuggingFaceEmbeddings:
    """Lazy singleton for the local sentence-transformers embedding model."""
    global _embeddings
    with _embeddings_lock:
        if _embeddings is None:
            _embeddings = HuggingFaceEmbeddings(
                model_name=get_settings().embedding_model_name,
            )
    return _embeddings


def get_chroma_persist_directory() -> str:
    return str(_backend_root() / get_settings().chroma_persist_dir)


def ensure_chroma_directory() -> None:
    Path(get_chroma_persist_directory()).mkdir(parents=True, exist_ok=True)


def get_vector_store() -> Chroma:
    """Open the persisted Chroma collection (creates on first write)."""
    ensure_chroma_directory()
    return Chroma(
        collection_name=CHROMA_COLLECTION_NAME,
        embedding_function=get_embedding_model(),
        persist_directory=get_chroma_persist_directory(),
    )


def ingest_document(file_path: Path | str, document_id: str) -> int:
    """
    Load a PDF (PyPDFLoader) or plain text file, split, embed, and add to ChromaDB.

    Returns the number of chunks stored.
    """
    path = Path(file_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    suffix = path.suffix.lower()
    if suffix == ".pdf":
        loader = PyPDFLoader(str(path))
    elif suffix == ".txt":
        loader = TextLoader(str(path), autodetect_encoding=True)
    else:
        raise ValueError("RAG ingestion only supports PDF and TXT files.")

    documents = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)

    for doc in chunks:
        doc.metadata["document_id"] = document_id
        doc.metadata["source_path"] = path.as_posix()

    if not chunks:
        logger.warning("No text extracted for document_id=%s", document_id)
        return 0

    store = get_vector_store()
    ids = [f"{document_id}_{i}" for i in range(len(chunks))]
    store.add_documents(chunks, ids=ids)
    logger.info("Ingested %s chunks for document_id=%s", len(chunks), document_id)
    return len(chunks)
