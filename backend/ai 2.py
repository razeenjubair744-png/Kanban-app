import json
import os
from typing import Dict, Optional

import httpx
from fastapi import HTTPException

from .schemas import AIRequest, AIResponse, BoardData

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "openrouter/free"


def _extract_json_block(text: str) -> Optional[str]:
    start_index = text.find("{")
    if start_index == -1:
        return None

    depth = 0
    for index in range(start_index, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start_index : index + 1]

    return None


def _build_messages(request: AIRequest) -> list[Dict[str, str]]:
    base = [
        {
            "role": "system",
            "content": (
                "You are a kanban board assistant."
                " You will respond with JSON only."
                " Include a top-level string field named 'message'."
                " Optionally include a 'boardUpdates' object holding the complete board state"
                " if the user's prompt should update the board."
                " Do not wrap the JSON in markdown code fences."
            ),
        },
        {
            "role": "user",
            "content": (
                "Here is the current board state as JSON:\n"
                f"{json.dumps(request.board.model_dump(), indent=2)}\n"
                "Use this state to answer the prompt and make board updates if needed."
            ),
        },
    ]
    if request.history:
        for turn in request.history:
            base.append({"role": turn.get("role", "user"), "content": turn.get("text", "")})
    base.append({"role": "user", "content": request.prompt})
    return base


def _parse_ai_response(content: str) -> AIResponse:
    trimmed = content.strip()
    json_text = None
    if trimmed.startswith("{") and trimmed.endswith("}"):
        json_text = trimmed
    else:
        json_text = _extract_json_block(trimmed)

    if json_text:
        try:
            payload = json.loads(json_text)
            board_updates = payload.get("boardUpdates")
            board_data = BoardData.model_validate(board_updates) if board_updates is not None else None
            return AIResponse(message=str(payload.get("message", trimmed)), boardUpdates=board_data)
        except Exception:
            pass

    return AIResponse(message=trimmed, boardUpdates=None)


def call_openrouter(request: AIRequest) -> AIResponse:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return AIResponse(
            message=(
                "OpenRouter is not configured. Set OPENROUTER_API_KEY in the environment"
                " or .env file to enable AI board suggestions."
            ),
            boardUpdates=None,
        )

    payload = {
        "model": MODEL_NAME,
        "messages": _build_messages(request),
        "temperature": 0.2,
        "max_tokens": 600,
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                OPENROUTER_URL,
                json=payload,
                headers={"Authorization": f"Bearer {api_key}"},
            )
            response.raise_for_status()
            data = response.json()
            text = data["choices"][0]["message"]["content"]
            return _parse_ai_response(text)
    except Exception as exc:
        import sys
        print(f"AI Error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return AIResponse(
            message=(
                "AI service could not be reached. Check OPENROUTER_API_KEY or network "
                "connectivity, and try again."
            ),
            boardUpdates=None,
        )
