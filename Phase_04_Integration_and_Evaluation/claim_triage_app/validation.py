import json
import re

from pydantic import ValidationError

from errors import OutputValidationError
from schemas import ClaimTriage

DECISION_PATTERN = re.compile(
    r"\b(?:claim|it)\s+(?:is|has been|should be|will be|can be)\s+"
    r"(?:approved|denied|rejected|accepted|paid)\b"
    r"|\b(?:approve|deny|reject|accept|pay)\s+(?:the|this)\s+claim\b",
    re.IGNORECASE,
)


def parse_json(raw: str) -> dict:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise OutputValidationError(
            [f"Response is not valid JSON ({exc.msg})."]
        ) from exc

    if not isinstance(data, dict):
        raise OutputValidationError(["Response must be a JSON object."])

    return data


def check_schema(data: dict) -> ClaimTriage:
    try:
        return ClaimTriage.model_validate(data)
    except ValidationError as exc:
        problems = []
        for error in exc.errors():
            field = ".".join(str(part) for part in error["loc"]) or "response"
            problems.append(f"{field}: {error['msg']}")
        raise OutputValidationError(problems) from exc


def check_business_rules(result: ClaimTriage) -> list[str]:
    problems = []

    if result.missing_information and not result.needs_human_review:
        problems.append(
            "needs_human_review must be true when missing_information is not empty."
        )

    if result.claim_type == "context-dependent" and not result.needs_human_review:
        problems.append(
            "needs_human_review must be true for context-dependent claims."
        )

    if DECISION_PATTERN.search(f"{result.summary} {result.rationale}"):
        problems.append(
            "summary and rationale must not approve, deny, or settle the claim."
        )

    return problems


def validate_output(raw: str) -> ClaimTriage:
    data = parse_json(raw)
    result = check_schema(data)

    problems = check_business_rules(result)
    if problems:
        raise OutputValidationError(problems)

    return result
