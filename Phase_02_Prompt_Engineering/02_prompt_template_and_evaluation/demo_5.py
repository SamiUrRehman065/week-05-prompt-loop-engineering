import json
import time

from ollama import chat

from claims_dataset import claims_dataset

MODEL = "qwen2.5:7b"

ALLOWED_CATEGORIES = [
    "Property Damage",
    "Vehicle Damage",
    "Medical Expense",
    "Theft",
    "Other",
]


def original_prompt(claim: str) -> str:
    return f"""
Classify this insurance claim and list any missing information.

Claim: {claim}

Return JSON with the keys:
category, summary, missing_information, priority, human_review
"""


def enhanced_prompt(claim: str) -> str:
    categories_text = "\n".join(
        f"- {category}" for category in ALLOWED_CATEGORIES
    )

    return f"""
ROLE:
You are a preliminary insurance-claim triage assistant.

OBJECTIVE:
Classify the claim and identify the evidence that is still missing.

ALLOWED CATEGORIES:
{categories_text}

EVIDENCE NORMALLY REQUIRED:
- Property Damage: incident date, damage extent, repair or damage estimate, photographs.
- Vehicle Damage: incident date, damage details, photographs, police report if another driver was involved.
- Theft: police report, theft date, list of stolen items, proof of ownership.
- Medical Expense: medical bill, accident details, treatment date.

RULES:
- Select exactly one category from the allowed list.
- Use only facts stated in the claim. Do not invent details.
- Compare the claim with the evidence list and report every item that is not mentioned.
- Do not approve or deny the claim.
- If no category fits, use "Other".

CLAIM:
<claim>
{claim}
</claim>

OUTPUT:
Return only a JSON object with these keys:
- "category": one allowed category
- "summary": one sentence
- "missing_information": list of strings
- "priority": "Low", "Medium", or "High"
- "human_review": true or false
"""


def run_model(prompt: str) -> tuple[str, float]:
    start = time.perf_counter()

    response = chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        format="json",
        options={"temperature": 0},
    )

    latency_seconds = time.perf_counter() - start
    return response.message.content, latency_seconds


def main():
    with open("results.jsonl", "w", encoding="utf-8") as output_file:
        for item in claims_dataset:
            for version, prompt_function in [
                ("original", original_prompt),
                ("enhanced", enhanced_prompt),
            ]:
                raw_output, latency = run_model(
                    prompt_function(item["claim"])
                )

                record = {
                    "id": item["id"],
                    "version": version,
                    "expected_category": item["expected_category"],
                    "required_missing": item["required_missing"],
                    "claim": item["claim"],
                    "raw_output": raw_output,
                    "latency_seconds": round(latency, 3),
                }

                output_file.write(
                    json.dumps(record, ensure_ascii=False) + "\n"
                )

                print(
                    f"Claim {item['id']} | {version} | "
                    f"{latency:.2f}s"
                )
                print(raw_output)
                print("-" * 60)

    print("\nSaved results to results.jsonl")
    print("Next step: python evaluate_results.py")


if __name__ == "__main__":
    main()
