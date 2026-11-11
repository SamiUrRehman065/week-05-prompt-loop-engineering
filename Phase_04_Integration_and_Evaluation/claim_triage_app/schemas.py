from typing import Literal

from pydantic import BaseModel, Field, field_validator

ClaimType = Literal[
    "vehicle",
    "property",
    "travel",
    "health",
    "other",
    "context-dependent",
]
Priority = Literal["low", "medium", "high"]
Status = Literal["success", "failed", "rejected", "error"]


class ClaimTriage(BaseModel):
    claim_type: ClaimType
    priority: Priority
    summary: str = Field(min_length=10, max_length=600)
    missing_information: list[str]
    needs_human_review: bool
    rationale: str = Field(min_length=5, max_length=600)

    @field_validator("claim_type", "priority", mode="before")
    @classmethod
    def normalise_label(cls, value):
        if isinstance(value, str):
            return value.strip().lower().replace("_", "-").replace(" ", "-")
        return value

    @field_validator("missing_information")
    @classmethod
    def drop_blank_items(cls, items: list[str]) -> list[str]:
        return [item.strip() for item in items if item.strip()]


class TriageOutcome(BaseModel):
    status: Status
    termination_reason: str
    result: ClaimTriage | None = None
    attempts: int = 0
    errors: list[str] = Field(default_factory=list)
    latency_seconds: float = 0.0
    prompt_tokens: int = 0
    output_tokens: int = 0
