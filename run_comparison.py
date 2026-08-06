import json
from pathlib import Path

from src.bias import BiasEvaluator


AB_FILE = Path("data/ab_test_suite.json")


def load_results():

    with open(AB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def main():

    print("=" * 60)
    print("A/B JUDGE COMPARISON")
    print("=" * 60)

    results = load_results()

    config_a_wins = 0
    config_b_wins = 0

    scores_a = []
    scores_b = []

    comparison = []

    for item in results:

        score_a = item["config_a_score"]
        score_b = item["config_b_score"]

        scores_a.append(score_a)
        scores_b.append(score_b)

        if score_a > score_b:
            winner = "A"
            config_a_wins += 1

        elif score_b > score_a:
            winner = "B"
            config_b_wins += 1

        else:
            winner = "Tie"

        comparison.append(
            {
                "winner_original": winner,
                "winner_reversed": item["winner_reversed"],
            }
        )

    total = len(results)

    flip_rate = BiasEvaluator.calculate_position_flip_rate(
        comparison
    )

    print("\n")
    print("=" * 60)
    print("RESULT")
    print("=" * 60)

    print(f"Config A Wins : {config_a_wins}")
    print(f"Config B Wins : {config_b_wins}")

    print(f"Position Flip Rate : {flip_rate}%")

    avg_a = round(sum(scores_a) / total, 2)
    avg_b = round(sum(scores_b) / total, 2)

    print(f"\nAverage Score A : {avg_a}")
    print(f"Average Score B : {avg_b}")

    if avg_a > avg_b:

        print("\nWinner : CONFIG A")

    elif avg_b > avg_a:

        print("\nWinner : CONFIG B")

    else:

        print("\nOverall Tie")


if __name__ == "__main__":
    main()