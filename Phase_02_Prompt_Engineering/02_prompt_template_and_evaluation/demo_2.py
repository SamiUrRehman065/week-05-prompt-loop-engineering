
def build_prompt(claim: str) -> str:
    allowed_categories = [
        "Property Damage",
        "Vehicle Damage",
        "Medical Expense",
        "Theft",
        "Other",
    ]

    categories_text = "\n".join(
        f"- {category}" for category in allowed_categories
    )

    return f"""
ROLE:
You are a preliminary insurance-claim triage assistant.

OBJECTIVE:
Classify the claim and identify missing information.

ALLOWED CLAIM CATEGORIES:
{categories_text}

RULES:
- Select exactly one category from the allowed list.
- Do not invent facts that are not in the claim.
- Do not approve or deny the claim.
- If the available information is insufficient, explain what is missing.
- Recommend human review when appropriate.
- If no category fits, select "Other" and explain why.

INPUT CLAIM:
<claim>
{claim}
</claim>

OUTPUT REQUIREMENTS:
Provide:
1. Claim category
2. Brief summary
3. Missing information
4. Priority: Low, Medium, or High
5. Human-review recommendation: Yes or No
"""


test_claims = [
    "A pipe burst in my house, but I have no repair estimate.",
    "My car was hit in a parking lot, and the other driver left.",
    "My laptop was stolen from my office, but I have no police report.",
]

if __name__ == "__main__":
    for index, claim in enumerate(test_claims, start=1):
        print(f"\n{'=' * 60}")
        print(f"TEST CLAIM {index}")
        print("=" * 60)
        print(build_prompt(claim))

