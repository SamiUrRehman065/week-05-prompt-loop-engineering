import time

from config import MAX_ATTEMPTS, MAX_TOTAL_SECONDS, RETRY_BASE_DELAY_SECONDS
from errors import (
    InvalidInputError,
    LLMServiceError,
    ModelUnavailableError,
    OutputValidationError,
)
from input_layer import clean_claim
from llm_client import OllamaClient
from prompt_layer import build_feedback, build_messages
from schemas import TriageOutcome
from validation import validate_output

TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "triage_claim",
        "description": (
            "Classify an insurance claim, summarise it, and list missing "
            "evidence. It never approves or denies a claim."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "claim_text": {
                    "type": "string",
                    "description": "The customer's description of the claim.",
                }
            },
            "required": ["claim_text"],
        },
    },
}


def triage_claim(
    claim_text: str,
    client: OllamaClient | None = None,
    max_attempts: int = MAX_ATTEMPTS,
) -> TriageOutcome:
    try:
        claim = clean_claim(claim_text)
    except InvalidInputError as exc:
        return TriageOutcome(
            status="rejected",
            termination_reason="invalid_input",
            errors=[str(exc)],
        )

    client = client or OllamaClient()
    start = time.perf_counter()
    errors = []
    attempts = 0
    prompt_tokens = 0
    output_tokens = 0
    previous_output = None
    feedback = None
    last_failure = None

    def finish(status, reason, result=None):
        return TriageOutcome(
            status=status,
            termination_reason=reason,
            result=result,
            attempts=attempts,
            errors=errors,
            latency_seconds=round(time.perf_counter() - start, 3),
            prompt_tokens=prompt_tokens,
            output_tokens=output_tokens,
        )

    while attempts < max_attempts:
        if time.perf_counter() - start > MAX_TOTAL_SECONDS:
            return finish("failed", "time_budget_exhausted")

        attempts += 1
        messages = build_messages(claim, previous_output, feedback)

        try:
            reply = client.chat_json(messages)
        except ModelUnavailableError as exc:
            errors.append(str(exc))
            return finish("error", "model_unavailable")
        except LLMServiceError as exc:
            errors.append(f"Attempt {attempts}: {exc}")
            last_failure = "service"
            if attempts < max_attempts:
                time.sleep(RETRY_BASE_DELAY_SECONDS * 2 ** (attempts - 1))
            continue

        prompt_tokens += reply.prompt_tokens
        output_tokens += reply.output_tokens

        try:
            result = validate_output(reply.content)
        except OutputValidationError as exc:
            errors.append(f"Attempt {attempts}: {exc}")
            last_failure = "validation"
            previous_output = reply.content
            feedback = build_feedback(exc.problems)
            continue

        return finish("success", "valid_output", result)

    if last_failure == "service":
        return finish("error", "service_unavailable")

    return finish("failed", "attempt_budget_exhausted")
