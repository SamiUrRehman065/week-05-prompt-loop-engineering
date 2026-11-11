
from ollama import chat

MODEL = "qwen2.5:7b"
MIN_WORDS = 40
MAX_ATTEMPTS = 3

CLAIM = """
A pipe burst in a house and damaged the kitchen ceiling.
Photographs are available, but a repair estimate has not
been obtained. The damage occurred yesterday.
"""


def generate_summary(feedback: str = "") -> str:
    prompt = f"""
Write a summary of the insurance claim below.

Requirements:
- At least {MIN_WORDS} words.
- Use only supplied facts.
- Identify missing information.
- Do not infer coverage or liability.
- Do not approve or deny the claim.

Claim:
{CLAIM}

{feedback}

Return only the summary.
"""

    response = chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0},
    )
    return response.message.content.strip()


def validate(text: str) -> tuple[bool, str]:
    word_count = len(text.split())

    if word_count < MIN_WORDS:
        return False, (
            f"Output has {word_count} words; "
            f"minimum is {MIN_WORDS}."
        )

    return True, f"Word count passed: {word_count}."


def main():
    feedback = ""

    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"\nAttempt {attempt}/{MAX_ATTEMPTS}")

        summary = generate_summary(feedback)
        valid, reason = validate(summary)

        print(summary)
        print("Validation:", reason)

        if valid:
            print("SUCCESS: returning validated output.")
            return

        feedback = (
            f"Your previous response failed validation: {reason} "
            "Revise it to satisfy the requirement without inventing facts."
        )

    print(
        f"\nFAILED: maximum of {MAX_ATTEMPTS} attempts reached. "
        "The last output must not be treated as validated."
    )


if __name__ == "__main__":
    main()

