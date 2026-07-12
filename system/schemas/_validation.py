from __future__ import annotations

from dataclasses import asdict, fields, is_dataclass
from datetime import datetime, timezone
from typing import Any, Mapping


class ValidationError(ValueError):
    """Raised when a schema payload violates system policy."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def require_non_empty(value: Any, field_name: str) -> None:
    if value is None or value == "" or value == [] or value == {}:
        raise ValidationError(f"{field_name} is required")


def reject_unknown_fields(data: Mapping[str, Any], allowed: set[str]) -> None:
    unknown = set(data) - allowed
    if unknown:
        joined = ", ".join(sorted(unknown))
        raise ValidationError(f"unknown field(s): {joined}")


def dataclass_to_dict(instance: Any) -> dict[str, Any]:
    if not is_dataclass(instance):
        raise TypeError("instance must be a dataclass")
    return asdict(instance)


def allowed_dataclass_fields(cls: type) -> set[str]:
    return {field.name for field in fields(cls)}


def default_metadata(workflow_id: str, source: str, created_by: str) -> dict[str, Any]:
    return {
        "workflow_id": workflow_id,
        "source": source,
        "created_at": utc_now(),
        "created_by": created_by,
    }


def has_required_metadata(metadata: Mapping[str, Any]) -> bool:
    return all(metadata.get(key) for key in ("workflow_id", "source", "created_at", "created_by"))
