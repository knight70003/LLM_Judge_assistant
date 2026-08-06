import json
from pathlib import Path

from src.judge import judge
from src.evaluator import EvaluationReport


TEST_SUITE = Path("data/test_suite.json")


def load_test_suite():
    with open(TEST_SUITE, "r", encoding="utf-8") as f:
        return json.load(f)


def main():

    print("=" * 60)
    print("LLM JUDGE EVALUATION")
    print("=" * 60)

    test_cases = load_test_suite()

    report = EvaluationReport()

    for case in test_cases:

        print(f"\nEvaluating : {case['id']}")

        judge_result = judge.evaluate_case(case)

        if not judge_result["success"]:
            print("Judge Failed")
            continue

        # judge.py already parsed the response
        verdict = judge_result["verdict"]

        # Skip malformed verdicts
        if not isinstance(verdict, dict):
            print("Parser Failed")
            continue

        if "overall_score" not in verdict:
            print("Parser Failed")
            continue

        if "pass_" not in verdict and "pass" in verdict:
            verdict["pass_"] = verdict.pop("pass")

        report.add_result(verdict)

        print(f"Overall Score : {verdict['overall_score']}")

    final_report = report.generate()

    print("\n")
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if final_report is None:
        print("No valid evaluation results.")
        return

    print(f"Total Cases : {final_report['total_cases']}")
    print(f"Pass Rate : {final_report['pass_rate']}%")
    print(f"Mean Score : {final_report['mean_score']}")

    print("\nReport Saved -> reports/report.json")


if __name__ == "__main__":
    main()