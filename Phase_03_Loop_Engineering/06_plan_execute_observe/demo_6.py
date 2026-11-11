
import json
from ollama import chat

MODEL = "qwen2.5:7b"
MAX_STEPS = 4

CLAIM = """
A pipe burst in my house. The kitchen ceiling is damaged.
I have photographs, but no repair estimate.
"""

TOOLS = {
    "extract_facts": (
        "Extract explicitly stated facts from the claim."
    ),
    "identify_missing_information": (
        "List information needed for further assessment."
    ),
    "classify_claim": (
        "Choose a claim category using the available facts."
    ),
    "finish": (
        "Finish the workflow."
    ),
}


def call_model(prompt: str, json_mode: bool = False) -> str:
    kwargs = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "options": {"temperature": 0},
    }

    if json_mode:
        kwargs["format"] = "json"

    response = chat(**kwargs)
    return response.message.content.strip()


def choose_action(state: dict) -> dict:
    prompt = f"""
You are controlling a small claim-analysis workflow.

Available actions:
{json.dumps(TOOLS, indent=2)}

Current state:
{json.dumps(state, indent=2)}

Choose exactly one action from the available actions.

Return JSON:
{{
  "action": "one allowed action",
  "reason": "short explanation"
}}

Do not include code or other actions.
"""

    raw = call_model(prompt, json_mode=True)
    decision = json.loads(raw)

    if decision.get("action") not in TOOLS:
        raise ValueError("Model selected an unknown action.")

    return decision


def execute_action(action: str, state: dict) -> dict:
    # These are local, predefined tool implementations.
    if action == "extract_facts":
        result = call_model(f"""
Extract only explicitly stated facts from this claim.
Do not infer missing details.

Claim:
{CLAIM}
""")
        state["facts"] = result

    elif action == "identify_missing_information":
        result = call_model(f"""
Identify missing information from the claim and extracted facts.

Claim:
{CLAIM}

Extracted facts:
{state.get("facts", "Not available")}

Return only a list of missing information.
""")
        state["missing_information"] = result

    elif action == "classify_claim":
        result = call_model(f"""
Classify this claim as vehicle, property, travel, health,
other, or context-dependent.

Claim:
{CLAIM}

Extracted facts:
{state.get("facts", "Not available")}

Missing information:
{state.get("missing_information", "Not available")}

Return one category and a short explanation.
Do not decide coverage or claim approval.
""")
        state["classification"] = result

    elif action == "finish":
        state["finished"] = True

    return state


def main():
    state = {
        "facts": "",
        "missing_information": "",
        "classification": "",
        "finished": False,
    }

    for step in range(1, MAX_STEPS + 1):
        print(f"\n--- STEP {step} ---")

        decision = choose_action(state)
        action = decision["action"]

        print("Chosen action:", action)
        print("Reason:", decision.get("reason", ""))

        if action == "finish":
            state["finished"] = True
            break

        state = execute_action(action, state)
        print("Updated state:", json.dumps(state, indent=2))

        # Prevent repeated actions from consuming the whole budget.
        # The model can choose only actions that are still needed.
        completed = {
            "extract_facts": bool(state["facts"]),
            "identify_missing_information": bool(
                state["missing_information"]
            ),
            "classify_claim": bool(state["classification"]),
        }

        if all(completed.values()):
            state["finished"] = True
            break

    print("\nFINAL STATE")
    print(json.dumps(state, indent=2))

    if not state["finished"]:
        print("Workflow stopped because the step budget was exhausted.")


if __name__ == "__main__":
    main()

