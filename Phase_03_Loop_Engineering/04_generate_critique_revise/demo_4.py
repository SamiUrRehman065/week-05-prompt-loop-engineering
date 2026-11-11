
from ollama import chat

MODEL = "qwen2.5:7b"

CLAIM = """
A pipe burst upstairs and damaged the kitchen ceiling.
The homeowner has photographs but no repair estimate.
The incident occurred yesterday.
"""


def ask_model(prompt: str) -> str:
    response = chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0},
    )
    return response.message.content.strip()


def main():
    # Stage 1: Generate.
    draft = ask_model(f"""
Write a concise preliminary summary of this claim.

Use only stated facts. Identify missing information.
Do not infer coverage or liability.

Claim:
{CLAIM}
""")

    print("\n--- DRAFT ---\n")
    print(draft)

    # Stage 2: Critique.
    critique = ask_model(f"""
Review the draft against the original claim.

Original claim:
{CLAIM}

Draft:
{draft}

Identify:
- Unsupported factual assertions.
- Important omitted facts.
- Missing information not identified.
- Any claim of coverage, liability, approval, or denial.

Do not rewrite the draft. Return a concise critique.
""")

    print("\n--- CRITIQUE ---\n")
    print(critique)

    # Stage 3: Revise.
    revised = ask_model(f"""
Revise the draft using the critique.

Original claim:
{CLAIM}

Draft:
{draft}

Critique:
{critique}

Rules:
- Preserve supported facts.
- Remove unsupported assertions.
- Identify missing information.
- Do not infer coverage or liability.
- Do not approve or deny the claim.
- If the critique is incorrect, do not follow it blindly.

Return only the revised summary.
""")

    print("\n--- REVISED SUMMARY ---\n")
    print(revised)


if __name__ == "__main__":
    main()

