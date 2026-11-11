import re

from config import MAX_CLAIM_LENGTH, MIN_CLAIM_LENGTH
from errors import InvalidInputError


def clean_claim(text: str | None) -> str:
    if text is None:
        raise InvalidInputError("No claim text was provided.")

    cleaned = re.sub(r"</?claim>", "", text, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    if not cleaned:
        raise InvalidInputError("Claim text is empty.")

    if not re.search(r"[A-Za-z]", cleaned):
        raise InvalidInputError("Claim text does not contain any words.")

    if len(cleaned) < MIN_CLAIM_LENGTH:
        raise InvalidInputError(
            f"Claim text is too short (minimum {MIN_CLAIM_LENGTH} characters)."
        )

    if len(cleaned) > MAX_CLAIM_LENGTH:
        raise InvalidInputError(
            f"Claim text is too long (maximum {MAX_CLAIM_LENGTH} characters)."
        )

    return cleaned
