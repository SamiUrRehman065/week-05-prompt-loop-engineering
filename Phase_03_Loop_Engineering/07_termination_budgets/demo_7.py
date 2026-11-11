
import time
from ollama import chat

MODEL = "qwen2.5:7b"
MAX_CALLS = 3
MAX_SECONDS = 90

CLAIM = """
A pipe burst and damaged the kitchen ceiling.
Photographs are available, but a repair estimate is missing.
"""


def ask_model(prompt: str) -> str:
    response = chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0},
    )
    return response.message.content.strip()


def main():
    start = time.monotonic()
    calls = 0
    result = ""
    feedback = ""

    while calls < MAX_CALLS:
        elapsed = time.monotonic() - start

        if elapsed >= MAX_SECONDS:
            print("Stopping: time budget exhausted.")
            break

        calls += 1
        print(f"\nCall {calls}/{MAX_CALLS}")

        result = ask_model(f"""
Produce a preliminary claim summary of 40 to 80 words.

Claim:
{CLAIM}

Previous feedback:
{feedback}

Do not invent facts or decide coverage.
Return only the summary.
""")

        print(result)

        word_count = len(result.split())
        print("Word count:", word_count)

        if 40 <= word_count <= 80:
            print("Stopping: validation succeeded.")
            break

        feedback = (
            f"Your previous response contained {word_count} words. "
            "Return a summary containing 40 to 80 words."
        )

    else:
        print("Stopping: call budget exhausted.")

    elapsed = time.monotonic() - start

    print("\n--- EXECUTION REPORT ---")
    print("Calls made:", calls)
    print(f"Elapsed time: {elapsed:.2f} seconds")
    print("Last output:", result or "(no output)")

    if not (40 <= len(result.split()) <= 80):
        print("Final status: output failed length validation.")
    else:
        print("Final status: length validation passed.")


if __name__ == "__main__":
    main()

