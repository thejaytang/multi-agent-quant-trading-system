from __future__ import annotations


def read_daily_signals(payload: dict | None = None) -> list[dict]:
    return (payload or {}).get("signals", [])
