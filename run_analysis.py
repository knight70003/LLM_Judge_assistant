"""
run_analysis.py

Runs:
- A/B Comparison
- Bias Analysis
- Judge Validation

Author: Tushar Verma
"""

from src.compare import ABComparison
from src.bias import BiasEvaluator
from src.validation import JudgeValidator


def main():

    print("=" * 60)
    print("LLM JUDGE ANALYSIS")
    print("=" * 60)

    # -------------------------------------------------
    # A/B Comparison
    # -------------------------------------------------

from pathlib import Path
import json
from src.pairwise_judge import pairwise_judge

comparison = ABComparison()

TEST_SUITE = Path("data/ab_test_suite.json")

with open(TEST_SUITE, "r", encoding="utf-8") as f:
    test_cases = json.load(f)

for case in test_cases:

    result = pairwise_judge.evaluate_pair(case)

    if result["success"]:

        comparison.add_result(
            result["score_a"],
            result["score_b"],
        )

report = comparison.generate_report()

print("\nA/B COMPARISON")
print("-" * 60)

print(f"Configuration A Average : {report['config_a_average']}")
print(f"Configuration B Average : {report['config_b_average']}")

print(f"Wins A : {report['wins_a']}")
print(f"Wins B : {report['wins_b']}")
print(f"Draws : {report['draws']}")

print(f"Winner : {report['winner']}")

    # -------------------------------------------------
    # Bias Analysis
    # -------------------------------------------------

bias_results = [

        {
            "winner_original": "A",
            "winner_reversed": "B",
            "verbose_wrong_selected": False,
            "accepted_confident_wrong": False,
        },

        {
            "winner_original": "A",
            "winner_reversed": "B",
            "verbose_wrong_selected": False,
            "accepted_confident_wrong": False,
        },

    ]

print("\nBIAS ANALYSIS")
print("-" * 60)

flip_rate = BiasEvaluator.calculate_position_flip_rate(
        bias_results
    )

verbosity = BiasEvaluator.verbosity_bias(
        bias_results
    )

sycophancy = BiasEvaluator.sycophancy_bias(
        bias_results
    )

print(f"Position Flip Rate : {flip_rate}%")
print(f"Verbosity Accuracy : {verbosity['accuracy']}%")
print(f"Sycophancy Accuracy : {sycophancy['accuracy']}%")

    # -------------------------------------------------
    # Validation
    # -------------------------------------------------

print("\nJUDGE VALIDATION")
print("-" * 60)

scores = [5.0, 5.0, 5.0]

validation = JudgeValidator.test_retest_consistency(
        scores
    )

agreement = JudgeValidator.agreement_rate(

        [True, True],

        [True, True],

    )

print(f"Runs : {validation['runs']}")
print(f"Average Score : {validation['average_score']}")
print(f"Consistency : {validation['consistency']}%")
print(f"Agreement Rate : {agreement}%")

print("\nAnalysis Completed Successfully.")


if __name__ == "__main__":
    main()