import csv
import json
from pathlib import Path

RESULTS_FILE = Path("results.jsonl")
REVIEW_FILE = Path("manual_review.csv")
REQUIRED_KEYS = {
    "category",
    "summary",
    "missing_information",
    "priority",
    "human_review",
}


def load_records(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def parse_output(raw_output: str) -> dict | None:
    try:
        data = json.loads(raw_output)
    except json.JSONDecodeError:
        return None

    if not isinstance(data, dict) or not REQUIRED_KEYS.issubset(data):
        return None

    if not isinstance(data["missing_information"], list):
        return None

    return data


def item_found(required_item: str, reported_items: list) -> bool:
    words = required_item.lower().split()

    for reported in reported_items:
        text = str(reported).lower()
        if all(word in text for word in words):
            return True

    return False


def summarise(records: list[dict]) -> dict:
    total = len(records)
    valid = 0
    correct = 0
    required_total = 0
    required_found = 0
    latency_total = 0.0

    for record in records:
        latency_total += record["latency_seconds"]
        required_total += len(record["required_missing"])
        data = parse_output(record["raw_output"])

        if data is None:
            continue

        valid += 1

        category = str(data["category"]).strip().lower()
        if category == record["expected_category"].lower():
            correct += 1

        for item in record["required_missing"]:
            if item_found(item, data["missing_information"]):
                required_found += 1

    return {
        "claims": total,
        "classification_accuracy": correct / total if total else 0,
        "missing_information_recall": (
            required_found / required_total if required_total else 0
        ),
        "valid_output_rate": valid / total if total else 0,
        "mean_latency_seconds": latency_total / total if total else 0,
    }


def write_review_sheet(records: list[dict]) -> None:
    with REVIEW_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "id",
            "version",
            "claim",
            "summary",
            "missing_information",
            "factual_assertions",
            "unsupported_assertions",
        ])

        for record in records:
            data = parse_output(record["raw_output"]) or {}
            writer.writerow([
                record["id"],
                record["version"],
                record["claim"],
                data.get("summary", "INVALID OUTPUT"),
                "; ".join(str(x) for x in data.get("missing_information", [])),
                "",
                "",
            ])


def main():
    if not RESULTS_FILE.exists():
        print("results.jsonl not found. Run demo_5.py first.")
        return

    records = load_records(RESULTS_FILE)

    print(f"{'Metric':<30}{'original':>12}{'enhanced':>12}")
    print("-" * 54)

    results = {
        version: summarise(
            [r for r in records if r["version"] == version]
        )
        for version in ["original", "enhanced"]
    }

    rows = [
        ("Classification accuracy", "classification_accuracy", "{:.0%}"),
        ("Missing-information recall", "missing_information_recall", "{:.0%}"),
        ("Valid-output rate", "valid_output_rate", "{:.0%}"),
        ("Mean latency (s)", "mean_latency_seconds", "{:.2f}"),
    ]

    for label, key, fmt in rows:
        original = fmt.format(results["original"][key])
        enhanced = fmt.format(results["enhanced"][key])
        print(f"{label:<30}{original:>12}{enhanced:>12}")

    write_review_sheet(records)

    print("\nUnsupported-claim rate has to be counted by hand.")
    print(f"Fill in the last two columns of {REVIEW_FILE} for each output.")


if __name__ == "__main__":
    main()
