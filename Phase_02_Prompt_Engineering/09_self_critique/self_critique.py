from ollama import chat

MODEL = "qwen2.5:7b"

SOURCE = """
The customer has provided photographs.
A repair estimate has not been supplied.
"""

DRAFT = """
The customer has submitted all required documents.
The claim should be approved.
"""

CRITERIA = """
1. Does each factual statement follow from the input?
2. Does the draft invent missing information?
3. Does it make an unauthorized final claim decision?
4. What should be corrected?
"""


def build_prompt() -> str:
    return f"""
You are reviewing a draft written about an insurance claim.

Source information:
{SOURCE}
Draft:
{DRAFT}
Evaluate the draft against these criteria and answer each one separately:
{CRITERIA}
Base every judgement only on the source information.
"""


def main():
    response = chat(
        model=MODEL,
        messages=[{"role": "user", "content": build_prompt()}],
        options={"temperature": 0},
    )
    critique = response.message.content.strip()

    print("SOURCE INFORMATION")
    print("-" * 60)
    print(SOURCE.strip())

    print("\nDRAFT")
    print("-" * 60)
    print(DRAFT.strip())

    print("\nMODEL CRITIQUE")
    print("-" * 60)
    print(critique)

    print("\nNow check the critique itself against the source information.")
    print("Is every point it makes supported, or did it introduce new errors?")


if __name__ == "__main__":
    main()
