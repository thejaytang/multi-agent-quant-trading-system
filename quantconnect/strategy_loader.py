from __future__ import annotations


def load_active_strategies(payload: dict | None = None) -> list[dict]:
    return (payload or {}).get("strategies", [])
