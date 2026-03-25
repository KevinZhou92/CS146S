from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, List, Optional

from dotenv import load_dotenv

try:  # The dependency is optional during local testing.
    from ollama import chat as ollama_chat
except ImportError:  # pragma: no cover - handled at runtime without ollama installed.
    ollama_chat = None

load_dotenv()
logger = logging.getLogger(__name__)

# Generated via Exercise 1 prompt – configure default model for LLM extraction.
DEFAULT_OLLAMA_MODEL = (
    os.getenv("OLLAMA_ACTION_MODEL") or os.getenv("OLLAMA_MODEL") or "llama3.1:8b"
)

# JSON schema instructing Ollama to emit a flat string array.
LLM_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "json_schema",
    "json_schema": {
        "name": "action_items_payload",
        "schema": {
            "type": "object",
            "properties": {
                "action_items": {
                    "type": "array",
                    "items": {"type": "string", "minLength": 1},
                    "minItems": 0,
                }
            },
            "required": ["action_items"],
            "additionalProperties": False,
        },
    },
}

LLM_SYSTEM_PROMPT = (
    "You are an expert project assistant. Read the user's meeting notes and "
    "return only concrete action items, phrased as imperative statements. "
    "Skip contextual chatter, decisions, or status updates."
)

BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)


def _is_action_line(line: str) -> bool:
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False


def extract_action_items(text: str) -> List[str]:
    lines = text.splitlines()
    extracted: List[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    # Deduplicate while preserving order
    return _dedupe_preserve_order(extracted)


def _looks_imperative(sentence: str) -> bool:
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    # Crude heuristic: treat these as imperative starters
    imperative_starters = {
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "investigate",
    }
    return first.lower() in imperative_starters


def extract_action_items_llm(text: str, *, model: Optional[str] = None) -> List[str]:
    """Use an Ollama model to extract action items with structured output.

    Generated for Week 2 Exercise 1 to introduce an LLM-powered extractor.
    """

    normalized_input = text.strip()
    if not normalized_input:
        return []

    if ollama_chat is None:
        logger.warning("Ollama client not installed; falling back to heuristic extraction.")
        return extract_action_items(text)

    model_name = model or DEFAULT_OLLAMA_MODEL
    if not model_name:
        raise RuntimeError(
            "No Ollama model configured. Set OLLAMA_ACTION_MODEL/OLLAMA_MODEL or pass `model`."
        )

    messages = [
        {"role": "system", "content": LLM_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "Extract only the actionable tasks from the following notes. "
                "Return one short imperative sentence per task.\n\n" + normalized_input
            ),
        },
    ]

    try:
        response = ollama_chat(
            model=model_name,
            messages=messages,
            format=LLM_RESPONSE_SCHEMA,
            options={"temperature": 0.1},
        )
    except Exception as exc:  # pragma: no cover - depends on local Ollama runtime.
        logger.warning(
            "Calling Ollama model '%s' failed (%s); using heuristic extraction fallback.",
            model_name,
            exc,
        )
        return extract_action_items(text)

    content = _extract_message_content(response)
    items = _coerce_action_items(content)
    if not items:
        # Fall back to heuristics so the caller still receives a best-effort list.
        return extract_action_items(text)
    return _dedupe_preserve_order(items)


def _extract_message_content(response: Any) -> Any:
    """Normalize the response payload to a raw string or list."""

    message = getattr(response, "message", None)
    if message is None:
        return response
    if hasattr(message, "content"):
        return message.content
    if isinstance(message, dict):
        return message.get("content")
    return message


def _coerce_action_items(payload: Any) -> List[str]:
    """Parse the model output into a list of cleaned strings."""

    data = payload
    if isinstance(payload, str):
        stripped = payload.strip()
        if stripped.startswith("```") and stripped.endswith("```"):
            stripped = stripped.strip("`")
            stripped = stripped.split("\n", 1)[-1]
        try:
            data = json.loads(stripped)
        except json.JSONDecodeError:
            return []

    if isinstance(data, dict):
        maybe_items = data.get("action_items") or data.get("items")
        if isinstance(maybe_items, list):
            data = maybe_items
        else:
            return []

    if isinstance(data, list):
        cleaned: List[str] = []
        for value in data:
            text = str(value).strip()
            if text:
                cleaned.append(text)
        return cleaned
    return []


def _dedupe_preserve_order(items: List[str]) -> List[str]:
    seen: set[str] = set()
    unique: List[str] = []
    for item in items:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item.strip())
    return unique
