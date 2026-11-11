
import time
from ollama import chat

MODEL = "qwen2.5:7b"

CLAIM = "A tree fell on my parked car."

PROMPTS = {
    "Prompt A - Concise": """
Classify this insurance claim as vehicle, property, health,
travel, or other.

Claim: A tree fell on my parked car.
""",
    "Prompt B - Noisy": """
You are an assistant. Be detailed. Think carefully.
Insurance is important. Claims may involve many situations.
Vehicles can be cars, buses, and trucks. Property can mean
buildings or belongings. Health claims may involve treatment.
Travel claims may involve luggage or cancellation.
Many things can happen to customers. Please classify the claim
carefully and explain everything relevant.

Claim: A tree fell on my parked car.
""",
}


def run_prompt(label, prompt):
    start = time.perf_counter()

    response = chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        options={"temperature": 0},
    )

    elapsed_ms = (time.perf_counter() - start) * 1000

    return {
        "label": label,
        "output": response.message.content.strip(),
        "latency_ms": round(elapsed_ms, 2),
    }


def main():
    for label, prompt in PROMPTS.items():
        result = run_prompt(label, prompt)

        print("\n" + "=" * 60)
        print(result["label"])
        print("=" * 60)
        print("Output:", result["output"])
        print("Latency:", result["latency_ms"], "ms")


if __name__ == "__main__":
    main()

