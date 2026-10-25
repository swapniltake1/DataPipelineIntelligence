"""Minimal JSONL audit logger for the local demo."""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

AUDIT_PATH = Path("logs/audit.jsonl")


def record_event(event: dict[str, Any], path: Path = AUDIT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        **event,
    }
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(payload, ensure_ascii=False) + "\n")
