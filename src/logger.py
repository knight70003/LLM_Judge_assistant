"""
logger.py

Logs every Judge API call for auditing.

Each request is stored as one JSON object
inside logs/judge_logs.jsonl
"""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "judge_logs.jsonl"


def log_judge_call(
    test_case_id,
    prompt,
    raw_response,
    latency_ms,
    prompt_tokens,
    completion_tokens,
    total_tokens,
):
    """
    Append one log entry.
    """

    log = {

        "timestamp": datetime.utcnow().isoformat(),

        "test_case_id": test_case_id,

        "latency_ms": latency_ms,

        "prompt_tokens": prompt_tokens,

        "completion_tokens": completion_tokens,

        "total_tokens": total_tokens,

        "prompt": prompt,

        "raw_response": raw_response,

    }

    with open(
        LOG_FILE,
        "a",
        encoding="utf-8",
    ) as f:

        f.write(
            json.dumps(
                log,
                ensure_ascii=False,
            )
        )

        f.write("\n")