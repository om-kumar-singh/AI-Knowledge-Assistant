"""Local HuggingFace text2text generation (FLAN-T5) for RAG answers — no external APIs."""

from __future__ import annotations

import logging
import threading
from collections.abc import Sequence

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


def _format_history_block(chat_history: Sequence[tuple[str, str]] | None) -> str:
    if not chat_history:
        return "(No prior messages in this session.)"
    max_total = get_settings().llm_max_history_chars
    lines: list[str] = []
    total = 0
    # Prefer recent turns when trimming: walk newest-first, then restore chronological order.
    for role, text in reversed(list(chat_history)):
        line = f"{role.capitalize()}: {text.strip()}"
        if total + len(line) + 1 > max_total:
            break
        lines.append(line)
        total += len(line) + 1
    lines.reverse()
    return "\n".join(lines) if lines else "(No prior messages in this session.)"


def _build_prompt(
    current_query: str,
    knowledge_context: str,
    chat_history: Sequence[tuple[str, str]] | None,
) -> str:
    history_block = _format_history_block(chat_history)
    return (
        "Answer the user's current message using the knowledge base context and prior "
        "conversation when helpful. Stay grounded in the knowledge base when it applies.\n"
        "Knowledge base context:\n"
        f"{knowledge_context}\n"
        "Conversation:\n"
        f"{history_block}\n"
        "Current user message:\n"
        f"{current_query}\n"
        "Answer:"
    )


def generate_answer(
    query: str,
    context: list[str] | None,
    *,
    chat_history: Sequence[tuple[str, str]] | None = None,
) -> str:
    """
    Build a RAG (+ optional memory) prompt and run FLAN-T5 locally.
    Pipeline/model loads once via module-level `_get_pipeline()` (not per call).

    `chat_history`: chronological (role, message) pairs for prior turns only (not `query`).
    """
    settings = get_settings()
    ctx = context if context is not None else []
    parts = [c.strip() for c in ctx if c is not None and str(c).strip()]
    context_str = "\n\n".join(parts)
    has_history = bool(chat_history)

    if not context_str and not has_history:
        return (
            "No relevant passages were retrieved from the knowledge base. "
            "Upload documents or try a different query."
        )

    if not context_str:
        context_str = "(No passages retrieved from documents for this query.)"

    if len(context_str) > settings.llm_max_context_chars:
        context_str = context_str[: settings.llm_max_context_chars].rsplit(" ", 1)[0] + "…"

    prompt = _build_prompt(query, context_str, chat_history)
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
