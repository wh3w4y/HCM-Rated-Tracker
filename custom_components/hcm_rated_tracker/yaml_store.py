from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date as date_cls
from pathlib import Path
from typing import Any

import yaml
from homeassistant.core import HomeAssistant
from homeassistant.util.dt import now

from .const import DEFAULT_YAML_REL_PATH

@dataclass
class RatedEntry:
    date: str
    title: str
    extra: str
    rating: int

@dataclass
class TrackerState:
    entries: list[RatedEntry] = field(default_factory=list)  # newest first
    recommendations: str = ""

def _today_iso(hass: HomeAssistant) -> str:
    return now(hass).date().isoformat()

def _validate_and_normalize_entries(hass: HomeAssistant, data: Any) -> list[RatedEntry]:
    if data is None:
        return []

    if not isinstance(data, dict):
        raise ValueError("books.yaml must be a mapping with a top-level 'entries' key")

    entries = data.get("entries", [])
    if not isinstance(entries, list):
        raise ValueError("'entries' in books.yaml must be a list")

    out: list[RatedEntry] = []
    for i, item in enumerate(entries):
        if not isinstance(item, dict):
            raise ValueError(f"Entry #{i+1} must be a mapping")

        title = str(item.get("title", "")).strip()
        author = str(item.get("author", item.get("extra", ""))).strip()
        rating = item.get("rating", 0)
        entry_date = str(item.get("date", "")).strip() or _today_iso(hass)

        if not title:
            raise ValueError(f"Entry #{i+1} is missing 'title'")

        try:
            rating_int = int(rating)
        except Exception as e:
            raise ValueError(f"Entry #{i+1} has invalid rating: {rating}") from e

        if rating_int < 0 or rating_int > 10:
            raise ValueError(f"Entry #{i+1} rating must be 0-10 (got {rating_int})")

        try:
            date_cls.fromisoformat(entry_date)
        except Exception as e:
            raise ValueError(f"Entry #{i+1} date must be YYYY-MM-DD (got {entry_date})") from e

        out.append(RatedEntry(date=entry_date, title=title, extra=author, rating=rating_int))

    out.sort(key=lambda e: (e.date, e.title.lower()), reverse=True)
    return out

def _state_to_yaml(state: TrackerState) -> dict[str, Any]:
    return {
        "entries": [
            {"date": e.date, "title": e.title, "author": e.extra, "rating": int(e.rating)}
            for e in state.entries
        ]
    }

class YamlStore:
    """YAML is the source of truth for the log."""

    def __init__(self, hass: HomeAssistant, rel_path: str = DEFAULT_YAML_REL_PATH) -> None:
        self.hass = hass
        self.rel_path = rel_path

    @property
    def path(self) -> Path:
        return Path(self.hass.config.path(self.rel_path))

    async def load(self) -> TrackerState:
        path = self.path
        if not path.exists():
            return TrackerState()

        raw = await self.hass.async_add_executor_job(path.read_text, "utf-8")
        data = yaml.safe_load(raw) or {}
        entries = _validate_and_normalize_entries(self.hass, data)
        return TrackerState(entries=entries, recommendations="")

    async def save(self, state: TrackerState) -> None:
        path = self.path
        path.parent.mkdir(parents=True, exist_ok=True)

        payload = _state_to_yaml(state)
        dumped = yaml.safe_dump(
            payload,
            sort_keys=False,
            allow_unicode=True,
            width=120,
            default_flow_style=False,
        )

        tmp = path.with_suffix(path.suffix + ".tmp")
        await self.hass.async_add_executor_job(tmp.write_text, dumped, "utf-8")
        await self.hass.async_add_executor_job(tmp.replace, path)
