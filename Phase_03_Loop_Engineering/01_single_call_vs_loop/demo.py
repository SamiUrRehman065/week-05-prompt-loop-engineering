
import time
from ollama import chat

MODEL = "qwen2.5:7b"
MIN_WORDS = 40
MAX_ATTEMPTS = 3

CLAIM = """
A pipe burst in a house on Monday evening. Water damaged the
kitchen ceiling and two cabinets. The homeowner has photographs
of the damage but has not obtained a repair estimate. A plumber
stopped the leak the same evening. The extent of hidden water
damage has not yet been assessed.
"""


def count_words(text: str) -> int:
    return len(text.split())


def generate_summary(claim: str, feedback: str = "") -> tuple[str, float]:
    prompt = f"""
You are a preliminary insurance-claim summarization assistant.

Summarize the claim using only the facts provided.

Requirements:
- Include the incident and known damage.
- Include available evidence.
- Identify important missing information.
- Do not invent facts.
- Do not approve or deny the claim.
- Produce at least {MIN_WORDS} words.

CLAIM:
{claim}

{feedback}

Return only the summary.
"""

    start = time.perf_counter()

    response = chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0},
    )

    elapsed = time.perf_counter() - start
    return response.message.content.strip(), elapsed


def validate_summary(summary: str) -> tuple[bool, str]:
    words = count_words(summary)

    if words < MIN_WORDS:
        return (
            False,
            f"Summary contains {words} words; "
            f"at least {MIN_WORDS} are required.",
        )

    return True, f"Summary passed the length check ({words} words)."


# --------------------------------------------------
# APPROACH A: One call, then validate
# --------------------------------------------------

def run_single_call() -> dict:
    summary, latency = generate_summary(CLAIM)
    valid, message = validate_summary(summary)

    return {
        "summary": summary,
        "valid": valid,
        "validation_message": message,
        "calls": 1,
        "latency": latency,
    }


# --------------------------------------------------
# APPROACH B: Retry until valid or limit reached
# --------------------------------------------------

def run_bounded_loop() -> dict:
    total_latency = 0.0
    feedback = ""
    last_summary = ""

    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"\nAttempt {attempt}/{MAX_ATTEMPTS}")

        summary, latency = generate_summary(CLAIM, feedback)
        total_latency += latency
        last_summary = summary

        valid, message = validate_summary(summary)

        print(f"Word count: {count_words(summary)}")
        print(f"Validation: {message}")

        if valid:
            return {
                "summary": summary,
                "valid": True,
                "validation_message": message,
                "calls": attempt,
                "latency": total_latency,
            }

        feedback = f"""
Your previous summary failed validation:
{message}

Revise the summary to meet the minimum word count.
Preserve factual accuracy. Do not add unsupported details.
"""

    # All permitted attempts were used.
    return {
        "summary": last_summary,
        "valid": False,
        "validation_message": (
            f"Validation failed after {MAX_ATTEMPTS} attempts. "
            "The application stopped at its attempt limit."
        ),
        "calls": MAX_ATTEMPTS,
        "latency": total_latency,
    }


def display_result(title: str, result: dict) -> None:
    print(f"\n{'=' * 65}")
    print(title)
    print("=" * 65)
    print(result["summary"])
    print(f"\nValid: {result['valid']}")
    print(f"Result: {result['validation_message']}")
    print(f"LLM calls: {result['calls']}")
    print(f"Total latency: {result['latency']:.3f} seconds")


def main():
    print("Running single-call approach...")
    single = run_single_call()
    display_result("APPROACH A: SINGLE CALL", single)

    print("\nRunning bounded-retry approach...")
    loop = run_bounded_loop()
    display_result("APPROACH B: BOUNDED RETRY LOOP", loop)


if __name__ == "__main__":
    main()

