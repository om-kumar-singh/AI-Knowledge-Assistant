"""Local HuggingFace text2text generation (FLAN-T5) for RAG answers — no external APIs."""

from __future__ import annotations

import logging
import threading

import torch
from transformers import pipeline

from core.config import get_settings

logger = logging.getLogger(__name__)

_pipeline_lock = threading.Lock()
_infer_lock = threading.Lock()
_pipeline = None


def _get_pipeline():
    """Load the transformers pipeline once (thread-safe)."""
    global _pipeline
    with _pipeline_lock:
        if _pipeline is None:
            settings = get_settings()
            logger.info("Loading local LLM: %s", settings.llm_model_name)
            common = {
                "task": "text2text-generation",
                "model": settings.llm_model_name,
                "model_kwargs": {"low_cpu_mem_usage": True},
            }
            if torch.cuda.is_available():
                _pipeline = pipeline(device_map="auto", **common)
            else:
                _pipeline = pipeline(device=-1, **common)
    return _pipeline


def _build_prompt(query: str, context: str) -> str:
    return (
        "Answer the question based only on the context below.\n"
        "Context:\n"
        f"{context}\n"
        "Question:\n"
        f"{query}\n"
        "Answer:"
    )


def generate_answer(query: str, context: list[str]) -> str:
    """
    Combine retrieved chunks, build a RAG prompt, and run FLAN-T5 locally.

    Context is length-limited before tokenization; generation uses max_new_tokens cap.
    """
    settings = get_settings()
    parts = [c.strip() for c in context if c and c.strip()]
    context_str = "\n\n".join(parts)
    if not context_str:
        return (
            "No relevant passages were retrieved from the knowledge base. "
            "Upload documents or try a different query."
        )

    if len(context_str) > settings.llm_max_context_chars:
        context_str = context_str[: settings.llm_max_context_chars].rsplit(" ", 1)[0] + "…"

    prompt = _build_prompt(query, context_str)
    pipe = _get_pipeline()

    with _infer_lock:
        outputs = pipe(
            prompt,
            max_new_tokens=settings.llm_max_new_tokens,
            do_sample=False,
            num_beams=1,
            truncation=True,
        )

    if not outputs:
        return ""

    text = outputs[0].get("generated_text", "")
    return text.strip() if isinstance(text, str) else str(text).strip()
