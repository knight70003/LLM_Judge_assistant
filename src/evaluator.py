"""
evaluator.py

Aggregates all parsed verdicts and generates
the final evaluation report.
"""

from __future__ import annotations

import json
from pathlib import Path


REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)

REPORT_FILE = REPORT_DIR / "report.json"


class EvaluationReport:

    def __init__(self):

        self.total_cases = 0

        self.passed_cases = 0

        self.failed_cases = 0

        self.total_score = 0

        self.criteria = {

            "correctness": 0,

            "faithfulness": 0,

            "completeness": 0,

            "instruction_following": 0,

            "tone_safety": 0,

        }

        self.results = []

    # -------------------------------------------------

    def add_result(self, verdict):

        self.total_cases += 1

        self.results.append(verdict)

        if verdict["pass_"]:

            self.passed_cases += 1

        else:

            self.failed_cases += 1

        self.total_score += verdict["overall_score"]

        self.criteria["correctness"] += verdict["correctness"]["score"]

        self.criteria["faithfulness"] += verdict["faithfulness"]["score"]

        self.criteria["completeness"] += verdict["completeness"]["score"]

        self.criteria["instruction_following"] += verdict["instruction_following"]["score"]

        self.criteria["tone_safety"] += verdict["tone_safety"]["score"]

    # -------------------------------------------------

    def generate(self):

        if self.total_cases == 0:

            return None

        report = {

            "total_cases": self.total_cases,

            "passed_cases": self.passed_cases,

            "failed_cases": self.failed_cases,

            "pass_rate": round(

                self.passed_cases / self.total_cases * 100,

                2,

            ),

            "mean_score": round(

                self.total_score / self.total_cases,

                2,

            ),

            "average_scores": {

                key: round(

                    value / self.total_cases,

                    2,

                )

                for key, value in self.criteria.items()

            },

            "results": self.results,

        }

        with open(

            REPORT_FILE,

            "w",

            encoding="utf-8",

        ) as f:

            json.dump(

                report,

                f,

                indent=4,

                ensure_ascii=False,

            )

        return report