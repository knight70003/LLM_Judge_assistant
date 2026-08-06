"""
validation.py

Judge validation utilities.

Implements:
- Test-Retest Consistency
- Gold Agreement (optional)
"""

from typing import List


class JudgeValidator:

    @staticmethod
    def test_retest_consistency(scores: List[float]) -> dict:
        """
        Measures how consistent the judge is across
        repeated evaluations of the same test case.
        """

        if not scores:
            return {
                "runs": 0,
                "average_score": 0,
                "consistency": 0,
            }

        average = sum(scores) / len(scores)

        tolerance = 0.5

        consistent = sum(
            abs(score - average) <= tolerance
            for score in scores
        )

        consistency = round(
            (consistent / len(scores)) * 100,
            2,
        )

        return {
            "runs": len(scores),
            "average_score": round(average, 2),
            "consistency": consistency,
        }

    @staticmethod
    def agreement_rate(predictions: List[bool], gold: List[bool]) -> float:
        """
        Computes agreement percentage with gold labels.
        """

        if not predictions or not gold:
            return 0.0

        if len(predictions) != len(gold):
            raise ValueError(
                "Predictions and gold labels must have equal length."
            )

        correct = sum(
            p == g
            for p, g in zip(predictions, gold)
        )

        return round(
            (correct / len(predictions)) * 100,
            2,
        )