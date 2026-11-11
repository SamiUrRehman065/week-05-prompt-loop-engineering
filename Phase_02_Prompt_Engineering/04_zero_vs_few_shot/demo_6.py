
import time
from ollama import chat

MODEL = "qwen2.5:7b"

# Three examples used only by the few-shot prompt.
FEW_SHOT_EXAMPLES = """
Example 1
Claim: My car collided with another car at an intersection.
Label: vehicle

Example 2
Claim: A water pipe burst and damaged my living room walls.
Label: property

Example 3
Claim: My suitcase went missing during an international flight.
Label: travel
"""

TEST_CLAIMS = [
    {
        "claim": "My car was hit by another driver in a parking lot.",
        "reference": "vehicle",
    },
    {
        "claim": "A pipe burst and flooded my kitchen.",
        "reference": "property",
    },
    {
        "claim": "My suitcase was lost during a flight.",
        "reference": "travel",
    },
    {
        "claim": "My laptop was damaged while I was using it at home.",
        "reference": "context-dependent",
    },
    {
        "claim": "I needed medical treatment after a road accident.",
        "reference": "context-dependent",
    },
]


def build_zero_shot_prompt(claim: str) -> str:
    return f"""
Classify the insurance-related claim into exactly one label:
vehicle, property, travel, health, other, or context-dependent.

Use context-dependent if the information is insufficient to determine
the intended category under the agreed label definitions.

Do not invent facts. Return only the label.

Claim: {claim}
Label:
"""


def build_few_shot_prompt(claim: str) -> str:
    return f"""
Classify the insurance-related claim into exactly one label:
vehicle, property, travel, health, other, or context-dependent.

Use context-dependent if the information is insufficient to determine
the intended category under the agreed label definitions.

Follow the classification pattern in these examples.

{FEW_SHOT_EXAMPLES}

Now classify this new claim.
Do not invent facts. Return only the label.

Claim: {claim}
Label:
"""


def classify(prompt: str) -> tuple[str, float]:
    start = time.perf_counter()

    response = chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0},
    )

    latency = time.perf_counter() - start
    label = response.message.content.strip().lower()

    return label, latency


results = []

for item in TEST_CLAIMS:
    zero_label, zero_time = classify(
        build_zero_shot_prompt(item["claim"])
    )

    few_label, few_time = classify(
        build_few_shot_prompt(item["claim"])
    )

    results.append({
        "claim": item["claim"],
        "zero_shot": zero_label,
        "few_shot": few_label,
        "reference": item["reference"],
        "zero_latency": zero_time,
        "few_latency": few_time,
    })


print("\nZERO-SHOT VS FEW-SHOT RESULTS")
print("=" * 100)

for result in results:
    print(f"\nTest input: {result['claim']}")
    print(f"Zero-shot result: {result['zero_shot']}")
    print(f"Few-shot result:  {result['few_shot']}")
    print(f"Reference label:  {result['reference']}")
    print(f"Zero-shot latency: {result['zero_latency']:.3f}s")
    print(f"Few-shot latency:  {result['few_latency']:.3f}s")

