"""Append-only JSON Lines audit logger."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

def record_event(event: dict[str, Any], path: Path | None = None) -> None:
    target = path or Path(os.getenv("AUDIT_LOG_PATH", "logs/audit.jsonl"))
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), **event}
    with target.open("a", encoding="utf-8") as file:
        file.write(json.dumps(payload, ensure_ascii=False) + "\n")
