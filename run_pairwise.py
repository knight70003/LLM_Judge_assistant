"""
run_pairwise.py

Runs Pairwise LLM Evaluation.

Evaluates:
- Response A vs Response B
- Response B vs Response A
- Position Bias
- Flip Rate

Author: Tushar Verma
"""

import json
from pathlib import Path

from src.pairwise_judge import pairwise_judge
from src.bias import BiasEvaluator


TEST_SUITE = Path("data/ab_test_suite.json")


def load_test_suite():

    with open(
        TEST_SUITE,
        "r",
        encoding="utf-8",
    ) as f:

        return json.load(f)


def main():

    print("=" * 60)
    print("PAIRWISE LLM JUDGE")
    print("=" * 60)

    test_cases = load_test_suite()

    bias_results = []

    for case in test_cases:

        print(f"\nEvaluating : {case['id']}")

        # -------------------------
        # Original Order
        # -------------------------

        original_case = {

            "id": case["id"],

            "input": case["input"],

            "system_prompt": case["system_prompt"],

            "response_a": case["response_a"],

            "response_b": case["response_b"],

        }

        result_original = pairwise_judge.evaluate_pair(
            original_case
        )

        if not result_original["success"]:

            print("Original Evaluation Failed")

            continue

        # -------------------------
        # Reverse Order
        # -------------------------

        reversed_case = {

            "id": case["id"] + "_reverse",

            "input": case["input"],

            "system_prompt": case["system_prompt"],

            "response_a": case["response_b"],

            "response_b": case["response_a"],

        }

        result_reverse = pairwise_judge.evaluate_pair(
            reversed_case
        )

        if not result_reverse["success"]:

            print("Reverse Evaluation Failed")

            continue

        winner_original = result_original["winner"]

        winner_reverse = result_reverse["winner"]

        print(f"Winner Original : {winner_original}")
        print(f"Winner Reverse  : {winner_reverse}")

        bias_results.append({

            "winner_original": winner_original,

            "winner_reversed": winner_reverse,

        })

    print("\n")
    print("=" * 60)
    print("POSITION BIAS REPORT")
    print("=" * 60)

    flip_rate = BiasEvaluator.calculate_position_flip_rate(
        bias_results
    )

    print(f"Total Cases : {len(bias_results)}")

    print(f"Position Flip Rate : {flip_rate}%")

    if flip_rate == 0:

        print("Judge is positionally consistent.")

    else:

        print("Position bias detected.")

    if winner_original == winner_reverse:
        final_winner = winner_original
        bias_flag = False
    else:
        final_winner = "Tie"
        bias_flag = True
    print(f"Final Winner : {final_winner}")
    print(f"Bias Flag    : {bias_flag}")

if __name__ == "__main__":
    main()