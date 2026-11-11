from ollama import chat

MODEL = "qwen2.5:7b"


def rule_classifier(text: str) -> str:
    text = text.lower()

    if "accident" in text or "collision" in text:
        return "vehicle accident"

    if "water leak" in text or "burst pipe" in text:
        return "property water damage"

    return "unknown"


examples = [
    "A delivery van struck my parked car.",
    "Water from a broken pipe damaged my kitchen.",
    "My car was damaged after another driver hit it.",
]

for example in examples:
    print("\nINPUT:", example)
    print("RULE:", rule_classifier(example))

    response = chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": (
                    "Classify this insurance claim in one short phrase. "
                    "Do not invent details.\n\n"
                    f"Claim: {example}"
                ),
            }
        ],
    )

    print("LLM:", response.message.content)
