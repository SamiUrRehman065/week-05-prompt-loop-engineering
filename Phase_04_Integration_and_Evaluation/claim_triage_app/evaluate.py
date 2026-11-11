import json
from collections import Counter
from pathlib import Path

from llm_client import OllamaClient
from triage import triage_claim

BASE_DIR = Path(__file__).parent
SAMPLES_FILE = BASE_DIR / "sample_claims.json"
REPORT_FILE = BASE_DIR / "evaluation_report.json"


def missing_item_found(expected: str, reported: list[str]) -> bool:
    words = expected.lower().split()
    return any(all(word in item.lower() for word in words) for item in reported)


def rate(part: int, whole: int) -> float:
    return round(part / whole, 3) if whole else 0.0


def evaluate_sample(sample: dict, client: OllamaClient) -> dict:
    outcome = triage_claim(sample["claim"], client=client)
    result = outcome.result

    expected_type = sample.get("expected_type")
    predicted_type = result.claim_type if result else None
    expected_missing = sample.get("expected_missing", [])

    found = []
    if result:
        found = [
            item for item in expected_missing
            if missing_item_found(item, result.missing_information)
        ]

    return {
        "id": sample["id"],
        "claim": sample["claim"],
        "status": outcome.status,
        "expected_status": sample.get("expected_status", "success"),
        "termination_reason": outcome.termination_reason,
        "expected_type": expected_type,
        "predicted_type": predicted_type,
        "type_correct": predicted_type == expected_type if expected_type else None,
        "expected_missing": expected_missing,
        "missing_found": found,
        "needs_human_review": result.needs_human_review if result else None,
        "attempts": outcome.attempts,
        "latency_seconds": outcome.latency_seconds,
        "prompt_tokens": outcome.prompt_tokens,
        "output_tokens": outcome.output_tokens,
        "errors": outcome.errors,
        "result": result.model_dump() if result else None,
    }


def summarise(rows: list[dict]) -> dict:
    typed = [r for r in rows if r["expected_type"]]
    expected_success = [r for r in rows if r["expected_status"] == "success"]
    succeeded = [r for r in rows if r["status"] == "success"]
    called = [r for r in rows if r["attempts"] > 0]

    expected_items = sum(len(r["expected_missing"]) for r in rows)
    found_items = sum(len(r["missing_found"]) for r in rows)

    return {
        "claims": len(rows),
        "status_as_expected_rate": rate(
            sum(r["status"] == r["expected_status"] for r in rows), len(rows)
        ),
        "classification_accuracy": rate(
            sum(bool(r["type_correct"]) for r in typed), len(typed)
        ),
        "valid_output_rate": rate(
            sum(r["status"] == "success" for r in expected_success),
            len(expected_success),
        ),
        "missing_information_recall": rate(found_items, expected_items),
        "human_review_rate": rate(
            sum(bool(r["needs_human_review"]) for r in succeeded), len(succeeded)
        ),
        "mean_attempts": rate(sum(r["attempts"] for r in called), len(called)),
        "mean_latency_seconds": rate(
            sum(r["latency_seconds"] for r in called), len(called)
        ),
        "total_prompt_tokens": sum(r["prompt_tokens"] for r in rows),
        "total_output_tokens": sum(r["output_tokens"] for r in rows),
        "termination_reasons": dict(
            Counter(r["termination_reason"] for r in rows)
        ),
    }


def main():
    samples = json.loads(SAMPLES_FILE.read_text(encoding="utf-8"))
    client = OllamaClient()
    rows = []

    for sample in samples:
        row = evaluate_sample(sample, client)
        rows.append(row)

        print(
            f"Claim {row['id']:>2} | {row['status']:<8} | "
            f"type: {str(row['predicted_type']):<17} "
            f"expected: {str(row['expected_type']):<17} | "
            f"attempts: {row['attempts']} | {row['latency_seconds']:.2f}s"
        )

    summary = summarise(rows)

    print("\nSUMMARY")
    print("=" * 50)
    for key, value in summary.items():
        print(f"{key:<28} {value}")

    REPORT_FILE.write_text(
        json.dumps({"summary": summary, "claims": rows}, indent=2),
        encoding="utf-8",
    )
    print(f"\nFull report saved to {REPORT_FILE.name}")


if __name__ == "__main__":
    main()
