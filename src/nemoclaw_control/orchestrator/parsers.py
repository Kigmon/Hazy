from __future__ import annotations

import json
from typing import Any


def parse_ollama_models(output: str) -> list[str]:
    models: list[str] = []
    for line in output.splitlines():
        if not line.strip() or line.lower().startswith("name"):
            continue
        parts = line.split()
        if parts:
            models.append(parts[0].strip())
    return models


def parse_json_or_empty(raw: str) -> dict[str, Any]:
    if not raw.strip():
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}
