import json
import re
from typing import Literal

from ollama import chat
from pydantic import BaseModel, ValidationError

MODEL = "qwen2.5:7b"

TEST_CLAIMS = [
    "My car was damaged in a collision. I do not have a repair estimate yet.",
    "A pipe burst and flooded my kitchen yesterday. I have photos and a plumber's invoice.",
    "My suitcase was lost during a flight.",
]

BROKEN_OUTPUTS = {
    "Not JSON": "claim_type: vehicle, priority: high",
    "Wrong field values": json.dumps({
        "claim_type": "car",
        "priority": "urgent",
        "summary": "Car damaged.",
        "missing_information": "Repair estimate",
        "needs_human_review": "maybe",
        "rationale": "Collision.",
    }),
    "Valid schema, wrong content": json.dumps({
        "claim_type": "vehicle",
        "priority": "high",
        "summary": "Vehicle damaged in a collision. The claim is approved.",
        "missing_information": ["Repair estimate"],
        "needs_human_review": False,
        "rationale": "Damage is confirmed.",
    }),
}


class ClaimResult(BaseModel):
    claim_type: Literal["vehicle", "property", "travel", "health", "other"]
    priority: Literal["low", "medium", "high"]
    summary: str
    missing_information: list[str]
    needs_human_review: bool
    rationale: str


def build_prompt(claim: str) -> str:
    return f"""
You are a preliminary insurance-claim triage assistant.

Read the claim and return a JSON object with exactly these fields:
- "claim_type": one of "vehicle", "property", "travel", "health", "other"
- "priority": one of "low", "medium", "high"
- "summary": one sentence using only stated facts
- "missing_information": list of evidence that is still needed
- "needs_human_review": true or false
- "rationale": short reason for the priority and review decision

Do not invent facts. Do not approve or deny the claim.

Claim:
<claim>
{claim}
</claim>
"""


def parse_check(raw: str) -> tuple[dict | None, str]:
    try:
        return json.loads(raw), "PASS"
    except json.JSONDecodeError as exc:
        return None, f"FAIL - not valid JSON ({exc.msg})"


def schema_check(data: dict) -> tuple[ClaimResult | None, str]:
    try:
        return ClaimResult.model_validate(data), "PASS"
    except ValidationError as exc:
        problems = [
            f"{'.'.join(str(p) for p in error['loc'])}: {error['msg']}"
            for error in exc.errors()
        ]
        return None, "FAIL - " + "; ".join(problems)


def semantic_check(result: ClaimResult) -> str:
    problems = []

    if result.missing_information and not result.needs_human_review:
        problems.append(
            "missing information is listed but human review is false"
        )

    text = f"{result.summary} {result.rationale}"
    if re.search(r"\b(approved|denied|rejected)\b", text, re.IGNORECASE):
        problems.append("output contains a claim decision")

    if problems:
        return "FAIL - " + "; ".join(problems)
    return "PASS"


def check(raw: str) -> None:
    data, parse_status = parse_check(raw)
    print("Parsing:          ", parse_status)
    if data is None:
        return

    result, schema_status = schema_check(data)
    print("Schema validation:", schema_status)
    if result is None:
        return

    print("Semantic checks:  ", semantic_check(result))


def ask_model(claim: str) -> str:
    response = chat(
        model=MODEL,
        messages=[{"role": "user", "content": build_prompt(claim)}],
        format="json",
        options={"temperature": 0},
    )
    return response.message.content.strip()


def main():
    print("PART 1: Hand-written outputs that should fail")
    for name, raw in BROKEN_OUTPUTS.items():
        print("\n" + "-" * 70)
        print(name)
        print(raw)
        check(raw)

    print("\n\nPART 2: Model outputs")
    for claim in TEST_CLAIMS:
        print("\n" + "-" * 70)
        print("Claim:", claim)
        raw = ask_model(claim)
        print(raw)
        check(raw)

    print("\nA PASS on all three checks does not prove every fact is correct.")
    print("Compare each summary with its claim before trusting it.")


if __name__ == "__main__":
    main()
