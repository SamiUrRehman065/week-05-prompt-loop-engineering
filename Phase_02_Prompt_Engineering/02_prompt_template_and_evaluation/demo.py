
def build_prompt(claim: str) -> str:
    return f"""
ROLE:
You are a preliminary insurance-claim triage assistant.

OBJECTIVE:
Categorize the claim and identify missing information.

CONSTRAINTS:
- Do not invent facts.
- Do not approve or deny claims.
- Recommend human review when appropriate.

INPUT:
<claim>
{claim}
</claim>

OUTPUT REQUIREMENTS:
Return the following:
- Claim category
- Summary
- Missing information
- Priority
- Human-review recommendation
"""


claim = (
    "A pipe burst in my house, "
    "but I have no repair estimate."
)

prompt = build_prompt(claim)
print(prompt)

