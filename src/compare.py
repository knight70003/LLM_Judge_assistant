"""
compare.py

Compares two configurations (Prompt V1 vs Prompt V2
or Model A vs Model B) using suite-level statistics.
"""

from statistics import mean


class ABComparison:

    def __init__(self):
        self.config_a_scores = []
        self.config_b_scores = []

    def add_result(self, score_a: float, score_b: float):
        self.config_a_scores.append(score_a)
        self.config_b_scores.append(score_b)

    def generate_report(self):

        total = len(self.config_a_scores)

        avg_a = mean(self.config_a_scores) if total else 0
        avg_b = mean(self.config_b_scores) if total else 0

        wins_a = 0
        wins_b = 0
        draws = 0

        for a, b in zip(self.config_a_scores, self.config_b_scores):

            if a > b:
                wins_a += 1

            elif b > a:
                wins_b += 1

            else:
                draws += 1

        if avg_a > avg_b:
            winner = "Configuration A"

        elif avg_b > avg_a:
            winner = "Configuration B"

        else:
            winner = "Tie"

        return {

            "config_a_average": round(avg_a, 2),

            "config_b_average": round(avg_b, 2),

            "wins_a": wins_a,

            "wins_b": wins_b,

            "draws": draws,

            "win_rate_a": round((wins_a / total) * 100, 2) if total else 0,

            "win_rate_b": round((wins_b / total) * 100, 2) if total else 0,

            "winner": winner

        }