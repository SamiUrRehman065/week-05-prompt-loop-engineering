
from ollama import chat

MODEL = "qwen2.5:7b"
MIN_WORDS = 40

CLAIM = """
A pipe burst in a house and damaged the kitchen ceiling.
Photographs are available, but a repair estimate has not
been obtained. The damage occurred yesterday.
"""


def generate_summary(claim: str) -> str:
    response = chat(
        model=MODEL,
        messages=[{
            "role": "user",
            "content": f"""
Summarize this claim in at least {MIN_WORDS} words.
Use only the supplied facts. Do not invent details.

Claim:
{claim}
""",
        }],
        options={"temperature": 0},
    )
    return response.message.content.strip()


def validate(summary: str) -> bool:
    return len(summary.split()) >= MIN_WORDS


def main():
    state = "START"
    summary = ""

    while state != "DONE":
        print(f"\nCurrent state: {state}")

        if state == "START":
            state = "GENERATE"

        elif state == "GENERATE":
            summary = generate_summary(CLAIM)
            print("Generated summary:", summary)
            state = "VALIDATE"

        elif state == "VALIDATE":
            if validate(summary):
                state = "SUCCESS"
            else:
                state = "FAILURE"

        elif state == "SUCCESS":
            print("Validation passed.")
            state = "DONE"

        elif state == "FAILURE":
            print("Validation failed. No retry is configured.")
            state = "DONE"

    print("\nFinal state:", state)


if __name__ == "__main__":
    main()

