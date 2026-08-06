"""
parser.py

Parses Judge LLM response.

Handles:
- Normal JSON
- Markdown JSON
- Malformed JSON
- Validation
"""

from __future__ import annotations

import json
import re
from typing import Dict, Any

from pydantic import BaseModel, ValidationError


# -----------------------------------------------------
# Pydantic Models
# -----------------------------------------------------

class Criterion(BaseModel):
    score: int
    rationale: str


class Verdict(BaseModel):
    correctness: Criterion
    faithfulness: Criterion
    completeness: Criterion
    instruction_following: Criterion
    tone_safety: Criterion

    overall_score: float
    pass_: bool
    overall_rationale: str


# -----------------------------------------------------
# JSON Extraction
# -----------------------------------------------------

def extract_json(raw: str) -> str:
    """
    Extract JSON object from model response.
    """

    raw = raw.strip()

    raw = raw.replace("```json", "")
    raw = raw.replace("```", "")

    match = re.search(r"\{.*\}", raw, re.DOTALL)

    if match:
        return match.group()

    return raw


# -----------------------------------------------------
# Parse Function
# -----------------------------------------------------

def parse_verdict(raw_response: str) -> Dict[str, Any]:

    try:

        cleaned = extract_json(raw_response)

        parsed = json.loads(cleaned)

        if "pass" in parsed:
            parsed["pass_"] = parsed.pop("pass")

        verdict = Verdict(**parsed)

        return {

            "success": True,

            "verdict": verdict.model_dump(),

        }

    except json.JSONDecodeError:

        return {

            "success": False,

            "error": "Invalid JSON",

            "raw_response": raw_response,

        }

    except ValidationError as e:

        return {

            "success": False,

            "error": "Schema Validation Failed",

            "details": str(e),

            "raw_response": raw_response,

        }

    except Exception as e:

        return {

            "success": False,

            "error": str(e),

            "raw_response": raw_response,

        }