"""
pairwise_judge.py

Pairwise LLM Judge

Compares Response A vs Response B
using Groq and returns the winner.

Author: Tushar Verma
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, Any

from groq import Groq

from config import (
    GROQ_API_KEY,
    JUDGE_MODEL,
    TEMPERATURE,
    MAX_OUTPUT_TOKENS,
)

from src.logger import log_judge_call


# -----------------------------------------------------
# Configure Groq
# -----------------------------------------------------

client = Groq(api_key=GROQ_API_KEY)


class PairwiseJudge:

    def __init__(self):

        self.client = Groq(
            api_key=GROQ_API_KEY
        )

        self.prompt_path = Path(
            "prompts/pairwise_prompt.txt"
        )

    # -------------------------------------------------

    def load_prompt_template(self) -> str:
        """
        Load pairwise prompt template.
        """

        return self.prompt_path.read_text(
            encoding="utf-8"
        )

    # -------------------------------------------------

    def build_prompt(
        self,
        test_case: Dict[str, Any],
    ) -> str:
        """
        Replace placeholders inside template.
        """

        template = self.load_prompt_template()

        template = template.replace(
            "{input}",
            test_case["input"],
        )

        template = template.replace(
            "{system_prompt}",
            test_case["system_prompt"],
        )

        template = template.replace(
            "{response_a}",
            test_case["response_a"],
        )

        template = template.replace(
            "{response_b}",
            test_case["response_b"],
        )

        return template

    # -------------------------------------------------

    def judge_pair(
        self,
        test_case: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Send pairwise evaluation request to Groq.
        """

        prompt = self.build_prompt(test_case)

        start_time = time.perf_counter()
        try:

            response = self.client.chat.completions.create(
                model=JUDGE_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=TEMPERATURE,
                max_completion_tokens=MAX_OUTPUT_TOKENS,
            )

            latency_ms = (
                time.perf_counter() - start_time
            ) * 1000

            raw_response = (
                response.choices[0]
                .message.content
            )

            try:

                cleaned = raw_response.strip()

                if cleaned.startswith("```json"):
                    cleaned = cleaned.replace(
                        "```json",
                        "",
                    )

                cleaned = cleaned.replace(
                    "```",
                    "",
                ).strip()

                start = cleaned.find("{")
                end = cleaned.rfind("}") + 1

                if start != -1 and end != -1:
                    cleaned = cleaned[start:end]

                parsed_json = json.loads(
                    cleaned
                )

            except Exception as e:

                print(
                    "\n========== PARSER ERROR =========="
                )
                print(e)
                print(raw_response)
                parsed_json = {
                    "response_a_score": 0,
                    "response_b_score": 0,
                    "winner": "Tie",
                    "reason": "Parser Failed",
                }

            prompt_tokens = None
            completion_tokens = None
            total_tokens = None
            try:
                usage = response.usage
                prompt_tokens = usage.prompt_tokens
                completion_tokens = usage.completion_tokens
                total_tokens = usage.total_tokens
            except Exception:
                pass

            log_judge_call(
                test_case_id=test_case["id"],
                prompt=prompt,
                raw_response=raw_response,
                latency_ms=latency_ms,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
            )

            return {

                "success": True,

                "score_a": parsed_json.get(
                    "response_a_score",
                    0,
                ),

                "score_b": parsed_json.get(
                    "response_b_score",
                    0,
                ),

                "winner": parsed_json.get(
                    "winner",
                    "Tie",
                ),

                "reason": parsed_json.get(
                    "reason",
                    "",
                ),

                "latency_ms": round(
                    latency_ms,
                    2,
                ),

                "raw_response": raw_response,

                "prompt_tokens": prompt_tokens,

                "completion_tokens": completion_tokens,

                "total_tokens": total_tokens,

            }

        except Exception as e:

            import traceback

            print("\n========== ERROR ==========")
            traceback.print_exc()
            print("===========================\n")

            return {

                "success": False,

                "error": str(e),

            }

    # -------------------------------------------------

    def evaluate_pair(
        self,
        test_case: Dict[str, Any],
        retries: int = 3,
    ) -> Dict[str, Any]:

        """
        Evaluate one pair of responses.

        Retries on temporary API failures.
        """

        last_error = None

        for attempt in range(
            1,
            retries + 1,
        ):

            result = self.judge_pair(
                test_case
            )

            if result["success"]:

                result["attempt"] = attempt

                return result

            last_error = result

            print(
                f"[Retry {attempt}/{retries}] "
                f"Pairwise Judge Failed..."
            )

            time.sleep(2)

        return {

            "success": False,

            "error": last_error.get(
                "error",
                "Unknown Error",
            ),

            "attempt": retries,

        }


# -----------------------------------------------------
# Singleton Instance
# -----------------------------------------------------

pairwise_judge = PairwiseJudge()