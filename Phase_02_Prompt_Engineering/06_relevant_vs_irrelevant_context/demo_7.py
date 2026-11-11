
import csv
import re
import time
from collections import Counter
from ollama import chat

MODEL = "qwen2.5:7b"
REPEATS = 3

CATEGORIES = [
    "vehicle",
    "property",
    "travel",
    "health",
    "other",
    "context-dependent",
]

# Context A: relevant information only.
RELEVANT_CONTEXT = """
Claim category definitions:
- vehicle: Damage to or collision involving a vehicle.
- property: Damage to a home, building, or household property.
- travel: Travel-related loss, such as lost luggage.
- health: Medical treatment or expenses.
- other: The claim does not fit the listed categories.
- context-dependent: The information is insufficient to assign
  a reliable category.
"""

# Context B: identical relevant context plus unrelated material.
IRRELEVANT_CONTEXT = RELEVANT_CONTEXT + """
Background paragraph 1 — Insurance history:
Insurance has a long history of transferring financial risk.
Different societies have developed many approaches to sharing
losses. Historical insurance practices changed over time as
commercial activity and legal systems developed.

Background paragraph 2 — Vehicle maintenance:
Vehicles may require oil changes, tire inspections, brake
maintenance, battery checks, and periodic servicing. Maintenance
schedules depend on vehicle type, age, usage, and manufacturer
recommendations.

Background paragraph 3 — Unrelated customer complaints:
Some customers complain about long telephone waiting times.
Others ask about website navigation, office opening hours,
billing notifications, or how to update their contact details.
These complaints are not necessarily related to an insurance claim.

Background paragraph 4 — General insurance administration:
Insurance organizations may use forms, customer portals,
document-management systems, and telephone support teams.
Administrative workflows vary between organizations.
"""

TEST_CLAIMS = [
    {
        "id": 1,
        "claim": "My car collided with another vehicle at a junction.",
        "reference": "vehicle",
    },
    {
        "id": 2,
        "claim": "A pipe burst and damaged the walls of my house.",
        "reference": "property",
    },
    {
        "id": 3,
        "claim": "My suitcase was lost during an international flight.",
        "reference": "travel",
    },
    {
        "id": 4,
        "claim": "I received medical treatment after an accident.",
        "reference": "health",
    },
    {
        "id": 5,
        "claim": "Something was damaged, but I have not explained what it was.",
        "reference": "context-dependent",
    },
]


def build_prompt(context: str, claim: str) -> str:
    return f"""
TASK:
Classify the claim using the supplied category definitions.

CONTEXT:
{context}

CLAIM:
<claim>
{claim}
</claim>

RULES:
- Use only the categories defined in the context.
- Do not invent facts.
- If the information is insufficient, use context-dependent.
- Return exactly one category label and nothing else.
"""


def normalize_label(output: str) -> str:
    text = output.strip().lower()
    text = text.replace("_", "-")

    # Accept a label even if the model adds a short explanation.
    for category in CATEGORIES:
        if re.search(
            rf"(?<![a-z-]){re.escape(category)}(?![a-z-])",
            text,
        ):
            return category

    return "invalid-output"


def run_once(context: str, claim: str) -> dict:
    prompt = build_prompt(context, claim)
    start = time.perf_counter()

    response = chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0},
    )

    latency = time.perf_counter() - start
    raw_output = response.message.content.strip()
    label = normalize_label(raw_output)

    return {
        "label": label,
        "latency_seconds": latency,
        "output_chars": len(raw_output),
        "raw_output": raw_output,
    }


results = []

# Run each claim against both context conditions.
for item in TEST_CLAIMS:
    for context_name, context in [
        ("A_relevant", RELEVANT_CONTEXT),
        ("B_extra_irrelevant", IRRELEVANT_CONTEXT),
    ]:
        for repeat in range(1, REPEATS + 1):
            result = run_once(context, item["claim"])

            record = {
                "claim_id": item["id"],
                "claim": item["claim"],
                "context": context_name,
                "repeat": repeat,
                "reference": item["reference"],
                **result,
            }
            results.append(record)

            print(
                f"Claim {item['id']} | {context_name} | "
                f"Run {repeat} | {result['label']} | "
                f"{result['latency_seconds']:.3f}s"
            )

# Save all individual runs so results can be inspected later.
with open(
    "context_results.csv",
    "w",
    newline="",
    encoding="utf-8",
) as file:
    writer = csv.DictWriter(
        file,
        fieldnames=results[0].keys(),
    )
    writer.writeheader()
    writer.writerows(results)


# Summarize each claim under each context condition.
print("\nSUMMARY")
print("=" * 80)

for item in TEST_CLAIMS:
    for context_name in ["A_relevant", "B_extra_irrelevant"]:
        group = [
            row for row in results
            if row["claim_id"] == item["id"]
            and row["context"] == context_name
        ]

        labels = [row["label"] for row in group]
        counts = Counter(labels)
        most_common_label, most_common_count = counts.most_common(1)[0]

        accuracy = sum(
            row["label"] == row["reference"]
            for row in group
        ) / len(group)

        mean_latency = sum(
            row["latency_seconds"] for row in group
        ) / len(group)

        mean_output_chars = sum(
            row["output_chars"] for row in group
        ) / len(group)

        consistency = most_common_count / len(group)

        print(
            f"Claim {item['id']} | {context_name} | "
            f"Accuracy: {accuracy:.0%} | "
            f"Consistency: {consistency:.0%} | "
            f"Mean latency: {mean_latency:.3f}s | "
            f"Mean output chars: {mean_output_chars:.1f}"
        )

print("\nDetailed results saved to context_results.csv")

