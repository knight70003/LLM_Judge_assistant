"""
bias.py

Bias evaluation utilities for the LLM Judge.
"""

from typing import List, Dict


class BiasEvaluator:

    @staticmethod
    def calculate_position_flip_rate(results: List[Dict]) -> float:
        """
        Calculates how often the winner changes
        when A/B order is reversed.
        """

        if not results:
            return 0.0

        flips = 0

        for item in results:

            if item["winner_original"] != item["winner_reversed"]:
                flips += 1

        return round(
            (flips / len(results)) * 100,
            2,
        )

    # ---------------------------------------------------

    @staticmethod
    def verbosity_bias(results: List[Dict]) -> Dict:

        fooled = 0

        for item in results:

            if item.get("verbose_wrong_selected", False):
                fooled += 1

        return {

            "total_cases": len(results),

            "fooled_cases": fooled,

            "accuracy": round(
                (len(results) - fooled)
                / len(results)
                * 100,
                2,
            )
            if results
            else 0,

        }

    # ---------------------------------------------------

    @staticmethod
    def sycophancy_bias(results: List[Dict]):

        fooled = 0

        for item in results:

            if item.get("accepted_confident_wrong", False):
                fooled += 1

        return {

            "fooled": fooled,

            "accuracy": round(
                (len(results) - fooled)
                / len(results)
                * 100,
                2,
            )
            if results
            else 0,

        }

    # ---------------------------------------------------

    @staticmethod
    def score_distribution(scores):

        if not scores:

            return {

                "min": 0,

                "max": 0,

                "average": 0,

            }

        return {

            "min": min(scores),

            "max": max(scores),

            "average": round(
                sum(scores) / len(scores),
                2,
            ),

        }